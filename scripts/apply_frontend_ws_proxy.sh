#!/usr/bin/env bash
# 192.168.168.149 SERVERIDA ishlatiladi (root yoki sudo bilan).
#
# Frontend nginx (https://...:3000) ga /api/v1/, /ws/, /go2rtc/, /media/, /assets/
# proxy location'larini qo'shadi — damafon/alerts WebSocket wss:// bo'lib ishlashi uchun.
# Sabab: frontend build https sahifada WS ni majburan wss:// ga o'giradi, backend
# nginx esa 8080 portda faqat plain HTTP (docker-compose: "8080:80").
#
# Ishlatish:
#   scp nginx/frontend-3000-proxy.conf scripts/apply_frontend_ws_proxy.sh root@192.168.168.149:/tmp/
#   ssh root@192.168.168.149 'bash /tmp/apply_frontend_ws_proxy.sh /tmp/frontend-3000-proxy.conf'
#
# Idempotent. Xatoda konfig backupdan tiklanadi va nginx tegilmagan holida qoladi.
set -euo pipefail

SNIPPET_SRC="${1:-/tmp/frontend-3000-proxy.conf}"
TARGET_NAME="frontend-3000-proxy.conf"
STAMP="$(date +%Y%m%d-%H%M%S)"
# 'listen ... 3000' — 'listen 13000' va 'return 301 ...:3000' ga tushmaydi.
LISTEN_RE='^[[:space:]]*listen[[:space:]]+([0-9.]*:|[[][0-9a-fA-F:]*[]]:)?3000[;[:space:]]'

log()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[x]\033[0m %s\n' "$*" >&2; exit 1; }

[ -f "$SNIPPET_SRC" ] || die "Snippet topilmadi: $SNIPPET_SRC"

# ------------------------------------------------------ 1. :3000 ni kim eshitadi
CONTAINER=""
if command -v docker >/dev/null 2>&1; then
    CONTAINER="$(docker ps --format '{{.ID}} {{.Ports}}' 2>/dev/null | awk '/:3000->/ {print $1; exit}')"
fi

if [ -n "$CONTAINER" ]; then
    log ":3000 docker konteynerda: $(docker inspect -f '{{.Name}}' "$CONTAINER" | sed 's#^/##') ($CONTAINER)"
    IN_DOCKER=1
else
    command -v nginx >/dev/null 2>&1 || die ":3000 uchun na docker konteyner, na host nginx topildi."
    log ":3000 host nginx da"
    IN_DOCKER=0
fi

run() {
    if [ "$IN_DOCKER" -eq 1 ]; then docker exec "$CONTAINER" "$@"; else "$@"; fi
}
copy_in() {
    if [ "$IN_DOCKER" -eq 1 ]; then docker cp "$1" "$CONTAINER:$2"; else install -m 0644 "$1" "$2"; fi
}

# --------------------------------------------------- 2. 'listen 3000' faylini top
CONF="$(run sh -c "grep -rlE '$LISTEN_RE' /etc/nginx 2>/dev/null | head -1" || true)"
CONF="$(printf '%s' "$CONF" | tr -d '\r')"
[ -n "$CONF" ] || die "/etc/nginx ichida 'listen ... 3000' topilmadi — konfig faylini qo'lda ko'rsating."
log "Konfig fayl: $CONF"

if run sh -c "grep -q '$TARGET_NAME' '$CONF'"; then
    warn "include allaqachon mavjud — faqat snippet yangilanadi."
    ALREADY=1
else
    ALREADY=0
fi

# ---------------------------------------------------------- 3. Backup + snippet
BACKUP="${CONF}.bak-${STAMP}"
run cp -a "$CONF" "$BACKUP"
log "Backup: $BACKUP"

run mkdir -p /etc/nginx/conf.d
copy_in "$SNIPPET_SRC" "/etc/nginx/conf.d/${TARGET_NAME}"
log "Snippet joylandi: /etc/nginx/conf.d/${TARGET_NAME}"

# ------------------------------------------------ 4. include ni server blokiga
# 'listen ... 3000' satridan KEYIN qo'yiladi — server bloki ichidagi eng xavfsiz
# nuqta (yopiluvchi qavsni topishga urinmaydi). nginx da location tartibi
# joylashuvga bog'liq emas: eng uzun prefiks yutadi.
# sed emas, awk — busybox (alpine) sed `0,/re/` ni bilmaydi.
if [ "$ALREADY" -eq 0 ]; then
    run sh -c "awk -v inc='    include /etc/nginx/conf.d/${TARGET_NAME};' '
        /$LISTEN_RE/ && !ins { print; print inc; ins=1; next }
        { print }
        END { if (!ins) exit 3 }
    ' '$CONF' > '$CONF.new'" \
      || { run rm -f "$CONF.new"; die "awk: 'listen ... 3000' satri topilmadi — o'zgarish qilinmadi."; }
    run sh -c "cat '$CONF.new' > '$CONF' && rm -f '$CONF.new'"
    log "include qo'shildi"
fi

# ------------------------------------------------------------ 5. Test + reload
if run nginx -t; then
    run nginx -s reload
    log "nginx reload qilindi"
else
    warn "nginx -t xato berdi — konfig backupdan tiklanmoqda"
    run sh -c "cat '$BACKUP' > '$CONF'"
    run nginx -t >/dev/null 2>&1 || warn "Diqqat: tiklangan konfig ham test o'tmadi!"
    die "O'zgarish bekor qilindi. Yuqoridagi 'nginx -t' xatosiga qarang."
fi

# -------------------------------------------------------------- 6. Tekshiruv
echo
log "Server bloki:"
run sh -c "grep -n -A4 -E '$LISTEN_RE' '$CONF'" || true
echo
echo "Mahalliy mashinadan:"
echo "  curl -sk -o /dev/null -w 'api: %{http_code}\n' https://192.168.168.149:3000/api/v1/"
echo "  # 401 => proxy ishlayapti (auth kerak, marshrut to'g'ri)"
