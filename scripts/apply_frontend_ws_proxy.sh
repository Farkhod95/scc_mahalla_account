#!/usr/bin/env bash
# 192.168.168.149 SERVERIDA ishlatiladi (root yoki sudo bilan).
#
# Frontend nginx (https://...:3000) ga /api/v1/, /ws/, /go2rtc/, /media/, /assets/
# proxy location'larini qo'shadi — damafon/alerts WebSocket wss:// bo'lib ishlashi uchun.
# Sabab: frontend build https sahifada WS ni majburan wss:// ga o'giradi, backend
# nginx esa 8080 portda faqat plain HTTP (docker-compose: "8080:80").
#
# Ishlatish (repo katalogidan):
#   sudo bash scripts/apply_frontend_ws_proxy.sh nginx/frontend-3000-proxy.conf
#
# Konfig avtomatik topilmasa, qo'lda ko'rsatish mumkin:
#   sudo CONF=/etc/nginx/conf.d/default.conf bash scripts/apply_frontend_ws_proxy.sh nginx/frontend-3000-proxy.conf
#
# Idempotent. Xatoda konfig backupdan tiklanadi, snippet o'chiriladi va nginx
# tegilmagan holida qoladi.
set -euo pipefail

SNIPPET_SRC="${1:-nginx/frontend-3000-proxy.conf}"
TARGET_NAME="frontend-3000-proxy.conf"

# DIQQAT: snippet `conf.d/` ga QO'YILMAYDI. nginx.conf da
# `include /etc/nginx/conf.d/*.conf;` bor — u yerdagi fayl `http` darajasida ham
# yuklanadi va `location` u kontekstda taqiqlangani uchun nginx ko'tarilmaydi
# ("location directive is not allowed here"). Shuning uchun `snippets/`.
SNIPPET_DIR="/etc/nginx/snippets"
SNIPPET_DST="${SNIPPET_DIR}/${TARGET_NAME}"
STALE_DST="/etc/nginx/conf.d/${TARGET_NAME}"   # eski, xato joylashuv

STAMP="$(date +%Y%m%d-%H%M%S)"
CONF="${CONF:-}"          # env orqali qo'lda ko'rsatish mumkin
BACKEND="192.168.168.149:8080"

log()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[x]\033[0m %s\n' "$*" >&2; exit 1; }

# 'listen <port>' — 'listen 1<port>' va 'return 301 ...:<port>' ga tushmaydi.
listen_re() {
    printf '^[[:space:]]*listen[[:space:]]+([0-9.]*:|[[][0-9a-fA-F:]*[]]:)?%s[;[:space:]]' "$1"
}

[ -f "$SNIPPET_SRC" ] || die "Snippet topilmadi: $SNIPPET_SRC"

# ------------------------------------------------------ 1. :3000 ni kim eshitadi
CONTAINER=""
if command -v docker >/dev/null 2>&1; then
    CONTAINER="$(docker ps --format '{{.ID}} {{.Ports}}' 2>/dev/null | awk '/:3000->/ {print $1; exit}')"
fi

# Konteyner ichidagi HAQIQIY port (docker 3000 ni 443/80 ga map qilgan bo'lishi mumkin)
PORTS="3000 443 80 8443"
if [ -n "$CONTAINER" ]; then
    log ":3000 docker konteynerda: $(docker inspect -f '{{.Name}}' "$CONTAINER" | sed 's#^/##') ($CONTAINER)"
    docker port "$CONTAINER" | sed 's/^/      /' || true
    INNER="$(docker port "$CONTAINER" 2>/dev/null | sed -n 's#^\([0-9]\{1,5\}\)/tcp[[:space:]]*->[[:space:]]*.*:3000$#\1#p' | head -1)"
    if [ -n "$INNER" ]; then
        log "Konteyner ichidagi port: $INNER  (host 3000 -> $INNER)"
        PORTS="$INNER 3000 443 80 8443"
    fi
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

# ------------------------- 0. Avvalgi muvaffaqiyatsiz urinish qoldig'ini tozalash
# Eski versiya snippet'ni conf.d/ ga qo'yardi — u yerda qolsa nginx ko'tarilmaydi.
if run sh -c "[ -f '$STALE_DST' ]" 2>/dev/null; then
    warn "Eski (xato joydagi) snippet topildi: $STALE_DST — o'chirilmoqda"
    run rm -f "$STALE_DST"
fi

# --------------------------------------------------- 2. Server konfigini topish
PORT=""
if [ -n "$CONF" ]; then
    log "Konfig qo'lda berildi: $CONF"
    for p in $PORTS; do
        if run sh -c "grep -qE '$(listen_re "$p")' '$CONF'"; then PORT="$p"; break; fi
    done
    [ -n "$PORT" ] || die "$CONF ichida ($PORTS) portlaridan hech biri uchun 'listen' satri topilmadi."
else
    for p in $PORTS; do
        f="$(run sh -c "grep -rlE '$(listen_re "$p")' /etc/nginx 2>/dev/null | head -1" || true)"
        f="$(printf '%s' "$f" | tr -d '\r')"
        if [ -n "$f" ]; then CONF="$f"; PORT="$p"; break; fi
    done
fi

if [ -z "$CONF" ]; then
    warn "/etc/nginx ichida mos 'listen' topilmadi. Mavjud 'listen' satrlari:"
    run sh -c "grep -rnE '^[[:space:]]*listen[[:space:]]' /etc/nginx 2>/dev/null | head -40" || true
    die "Kerakli faylni CONF=... bilan qo'lda ko'rsating."
fi
log "Konfig fayl: $CONF   (listen $PORT)"
LISTEN_RE="$(listen_re "$PORT")"

# Konteyner ichidagi o'zgarish DOIMIY bo'lishi uchun konfig bind-mount bo'lishi kerak,
# aks holda `docker compose up -d --build` da yo'qoladi.
if [ "$IN_DOCKER" -eq 1 ]; then
    echo
    log "Konteyner mount'lari (Destination):"
    docker inspect --format '{{range .Mounts}}{{println "     " .Destination "<-" .Source}}{{end}}' "$CONTAINER" || true
    MOUNTED=0
    while IFS= read -r dest; do
        [ -n "$dest" ] || continue
        [ "$CONF" = "$dest" ] && MOUNTED=1
        case "$CONF" in "$dest"/*) MOUNTED=1 ;; esac
        case "$SNIPPET_DIR" in "$dest"|"$dest"/*) MOUNTED=1 ;; esac
    done <<EOF
$(docker inspect --format '{{range .Mounts}}{{println .Destination}}{{end}}' "$CONTAINER" 2>/dev/null || true)
EOF
    if [ "$MOUNTED" -eq 1 ]; then
        log "Konfig bind-mount ichida — o'zgarish konteyner qayta yaratilsa ham saqlanadi"
    else
        warn "DIQQAT: konfig bind-mount EMAS. Bu o'zgarish faqat hozirgi konteynerda yashaydi va"
        warn "  'docker compose up -d --build' da YO'QOLADI. Doimiy qilish uchun snippet'ni"
        warn "  frontend repo'siga (nginx konfigi yoniga) qo'shib, image'ni qayta build qiling."
    fi
    echo
fi

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

run mkdir -p "$SNIPPET_DIR"
copy_in "$SNIPPET_SRC" "$SNIPPET_DST"
log "Snippet joylandi: $SNIPPET_DST"

# Xatoda hammasini joyiga qaytarish
rollback() {
    warn "Konfig backupdan tiklanmoqda va snippet o'chirilmoqda"
    run sh -c "cat '$BACKUP' > '$CONF'" || true
    run rm -f "$SNIPPET_DST" || true
    if run nginx -t >/dev/null 2>&1; then
        log "nginx konfigi yana toza (test o'tdi) — sayt ishlashda davom etadi"
    else
        warn "Diqqat: tiklangandan keyin ham 'nginx -t' o'tmadi:"
        run nginx -t || true
    fi
}

# Backend'ga (8080) shu joydan yetib borishini tekshirish — majburiy emas.
# 401 ham "ulanish bor" degani, shuning uchun javob HEADER i bo'yicha tekshiriladi.
if run sh -c "command -v wget >/dev/null 2>&1"; then
    CHK="$(run sh -c "wget -T 5 -S -O /dev/null 'http://${BACKEND}/api/v1/' 2>&1" || true)"
    case "$CHK" in
        *HTTP/1*) log "Backend http://${BACKEND} shu joydan ko'rinadi (javob keldi)" ;;
        *)        warn "Backend http://${BACKEND} ga ulanib bo'lmadi: $(printf '%s' "$CHK" | tr '\n' ' ' | cut -c1-160)" ;;
    esac
fi

# ------------------------------------------------ 4. include ni server blokiga
# 'listen ... <PORT>' satridan KEYIN qo'yiladi — server bloki ichidagi eng xavfsiz
# nuqta (yopiluvchi qavsni topishga urinmaydi). nginx da location tartibi
# joylashuvga bog'liq emas: eng uzun prefiks yutadi.
# sed emas, awk — busybox (alpine) sed `0,/re/` ni bilmaydi.
if [ "$ALREADY" -eq 0 ]; then
    if ! run sh -c "awk -v inc='    include ${SNIPPET_DST};' '
        /$LISTEN_RE/ && !ins { print; print inc; ins=1; next }
        { print }
        END { if (!ins) exit 3 }
    ' '$CONF' > '$CONF.new'"; then
        run rm -f "$CONF.new" || true
        run rm -f "$SNIPPET_DST" || true
        die "awk: 'listen ... $PORT' satri topilmadi — o'zgarish qilinmadi."
    fi
    run sh -c "cat '$CONF.new' > '$CONF' && rm -f '$CONF.new'"
    log "include qo'shildi: $SNIPPET_DST"
fi

# ------------------------------------------------------------ 5. Test + reload
if run nginx -t; then
    run nginx -s reload
    log "nginx reload qilindi"
else
    rollback
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
