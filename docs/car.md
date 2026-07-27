# Camera Server — Hudud monitoringi (ANPR)

Hududga **kirgan va chiqgan mashinalarni** monitoring qiluvchi server. Hikvision va Dahua
ANPR (avtomobil raqamini tanish) kameralariga ulanadi, aniqlangan voqealarni web panelda
jonli ko'rsatadi va har bir guruhning URL'iga POST qilib yuboradi. Barcha sozlamalar
(guruhlar, kameralar) **web orqali** kiritiladi va SQLite bazada saqlanadi.

---

## 1. Tezkor boshlash

```bash
# Build (Qt 6.10.2 + SDK lar o'rnatilgan bo'lsa)
cd /home/husan/Projects/Qt/DRB
/opt/Qt/6.10.2/gcc_64/bin/qmake -o build/Makefile Server.pro
make -C build -j$(nproc)

# Ishga tushirish
./build/Server --db data.db --http-port 8080 --user admin --password SIZNING_PAROL
```

So'ng brauzerda oching: **http://localhost:8080** (yoki tarmoqdan `http://<server-IP>:8080`).
Login va parol bilan kiring.

> Parol berilmasa, vaqtincha **admin / admin** ishlatiladi (logда ogohlantirish chiqadi).
> Birinchi kirishdan keyin **Sozlamalar** bo'limidan parolni o'zgartiring.

---

## 2. Ishga tushirish parametrlari

| Parametr | Tavsif | Default |
|----------|--------|---------|
| `--db <fayl>` | SQLite baza fayli | `data.db` |
| `--http-port <port>` | Web/HTTP port | `8080` |
| `--user <login>` | Panel login | `admin` |
| `--password <parol>` | Panel parol | `admin` (ogohlantirish bilan) |

Login/parolni muhit o'zgaruvchilari orqali ham berish mumkin:

```bash
CAMSERVER_USER=admin CAMSERVER_PASSWORD=maxfiy ./build/Server --db data.db --http-port 8080
```

Ustuvorlik tartibi: `--user/--password` → muhit o'zgaruvchilari → bazadagi saqlangan qiymat → `admin`.
Kiritilgan qiymatlar bazaga saqlanadi (keyingi safar qayta berish shart emas).

---

## 3. Web panel

Tepada 4 ta bo'lim (tab) bor:

### 3.1 Eventlar (monitoring)
Kameralardan kelgan oxirgi aniqlashlar **jonli** ko'rinadi (har 4 soniyada yangilanadi):
**vaqt, kamera IP, davlat raqami, yo'nalish (Kirdi/Chiqdi), mashina rasmi**.
Yuqorida "Kirdi" va "Chiqdi" sonlari hisobi chiqadi.

> ⚠️ Eventlar **bazaga saqlanmaydi** — faqat xotirada (oxirgi ~100 ta) turadi va guruh
> URL'iga yuboriladi. Server qayta ishga tushsa, ro'yxat tozalanadi.

### 3.2 Kameralar
Kameralar ro'yxati: IP, model, port, guruh, yo'nalish, **holat** (🟢 ulangan / 🔴 uzilgan /
⚪ noma'lum) va **Reconnect (24s)** — oxirgi 24 soatdagi qayta ulanishlar soni.

- **Yangi kamera** qo'shish: guruh, IP, port (`auto` = hikvision 8000 / dahua 37777), model,
  login, parol, yo'nalish, tezlik limiti.
- **Tahrir** — to'liq forma (modal): barcha maydonlar, jumladan kamerani **boshqa guruhga
  ko'chirish**. Parol maydonini bo'sh qoldirsangiz eski parol saqlanadi.
- **Yangilash** tugmasi holat va reconnect sonini yangilaydi.

### 3.3 Guruhlar
Har bir guruh = **izoh (nom) + market (max 256) + POST URL**. Shu guruhga biriktirilgan
kameralardan kelgan eventlar shu URL'ga yuboriladi (`group` va `market` ham payloadда ketadi).
CRUD: qo'shish, tahrir, o'chirish (guruh o'chsa, undagi kameralar ham o'chadi).

### 3.4 Sozlamalar
- **API key** — guruh URL'iga so'rov yuborilganda `X-Api-Key` header sifatida qo'shiladi.
- **location_type, region_soato** — hozir POST tanasiga kiritilmaydi (kelajak uchun qoldirilgan).
- **Login / parol** — kirish ma'lumotlarini o'zgartirish.

---

## 4. Tipik ish tartibi

1. **Sozlamalar** → kerak bo'lsa API key kiriting va parolni o'zgartiring.
2. **Guruhlar** → yangi guruh yarating (izoh + server POST URL'i).
3. **Kameralar** → guruhga kamera qo'shing (IP, model, login/parol, yo'nalish).
4. Kamera ulangach — **Eventlar** bo'limida raqam va rasm jonli ko'rinadi; har event guruh
   URL'iga POST qilinadi.
5. **Kameralar** bo'limida ulanish holati va reconnect sonini kuzating.

---

## 5. Guruh URL'iga yuboriladigan POST

Har bir ANPR voqea kameraning guruhidagi URL'ga **JSON** ko'rinishida POST qilinadi:

```json
{
  "date": "2026-06-22 12:00:00",
  "duration": "in",
  "plate": "01A123BC",
  "ip": "10.6.204.79",
  "group": "Malika kirish",
  "market": "Malika savdo markazi",
  "image": "<base64 JPEG>"
}
```

| Maydon | Ma'no |
|--------|-------|
| `date` | Kamera bergan voqea vaqti |
| `duration` | Yo'nalish (`in`/`out`); aniqlanmasa kameraning sozlangan qiymati |
| `plate` | Davlat raqami |
| `ip` | Kamera IP manzili |
| `group` | Guruh nomi (izoh) |
| `market` | Guruhning market nomi (max 256) |
| `image` | Mashina rasmi, base64 (bo'lmasa bo'sh) |

Header: `Content-Type: application/json` va (agar Sozlamalarda kiritilgan bo'lsa) `X-Api-Key`.

---

## 6. Avtomatik qayta ulanish (reconnect)

- **Hikvision** — SDK darajasida avto-reconnect yoqilgan; holat doimiy tekshiriladi.
- **Dahua** — SDK `CLIENT_SetAutoReconnect` orqali avto-reconnect.

Har bir ulanish/uzilish/qayta ulanish `connection_log` jadvaliga yoziladi va **24 soat**
saqlanadi (eskisi avtomatik o'chadi). Har kamera uchun oxirgi 24 soatdagi reconnect soni
**Kameralar** bo'limida va `GET /api/status` da ko'rinadi.

---

## 7. Ma'lumotlar saqlash

SQLite baza (`--db`) ichida:

| Jadval | Saqlanadi |
|--------|-----------|
| `groups` | guruhlar (izoh, POST URL) |
| `cameras` | kameralar (ip, port, model, login, parol, yo'nalish, holat) |
| `settings` | API key, login/parol, va h.k. |
| `connection_log` | ulanish tarixi — **24 soat** |

> ANPR eventlar va rasmlar **bazaga umuman yozilmaydi** (faqat jonli ko'rsatiladi va
> guruh URL'iga yuboriladi).

---

## 8. REST API

Avval token oling, so'ng har so'rovga `Authorization: Bearer <token>` qo'shing.

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8080/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"PAROL"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')

# Guruhlar
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/groups
curl -H "Authorization: Bearer $TOKEN" -X POST http://localhost:8080/api/groups \
  -H 'Content-Type: application/json' -d '{"description":"Kirish","post_url":"http://server/api/"}'
```

| Metod / yo'l | Vazifa |
|--------------|--------|
| `POST /api/login` | `{username,password}` → `{token}` |
| `GET/PUT /api/settings` | global sozlamalar (API key, login) |
| `GET/POST /api/groups` | guruhlar ro'yxati / qo'shish |
| `GET/PUT/DELETE /api/groups/{id}` | bitta guruh (kameralari bilan) |
| `GET/POST /api/cameras[?group_id=]` | kameralar / qo'shish |
| `GET/PUT/DELETE /api/cameras/{id}` | bitta kamera |
| `GET /api/status` | kameralar holati + reconnect soni |
| `GET /api/events` | jonli eventlar (xotiradan) |
| `GET /api/events/{id}/image` | event rasmi (JPEG); `?token=` ham qabul qilinadi |

Eslatma: rasm URL'i `?token=<token>` ni ham qabul qiladi (oddiy `<img>` tegi uchun).

---

## 9. Docker

```bash
# Image yig'ish (binary build/ da tayyor bo'lishi kerak)
bash docker/build.sh

# Ishga tushirish (kamera LAN'i uchun --net=host)
docker run -d --name camera-server --net=host \
  -e CAMSERVER_USER=admin -e CAMSERVER_PASSWORD=maxfiy \
  -v $PWD/data:/app/data \
  camera-server:latest
```

- Port: **8080** (`EXPOSE 8080`).
- Baza: `/app/data/data.db` — `-v` bilan saqlanadi (qayta ishga tushganda yo'qolmaydi).
- `--net=host` — kameralarga ichki tarmoqdan ulanish uchun.

---

## 10. Build (manbadan)

Talablar:
- **Qt 6.10.2** (`/opt/Qt/6.10.2/gcc_64`) — `core network httpserver sql concurrent` modullari.
- **Hikvision SDK** va **Dahua SDK** — yo'llar `Server.pro` da ko'rsatilgan.

```bash
/opt/Qt/6.10.2/gcc_64/bin/qmake -o build/Makefile Server.pro
make -C build -j$(nproc)        # natija: build/Server
```

Loyiha tuzilmasi:

```
main.cpp                  — bootstrap, event/holat callbacklari
cameraManager/            — Hikvision, DahuaANPR (SDK), CameraManager, EventDispatcher
core/ForwardingService.*  — guruh URL'iga POST
core/ConfigController.*    — DB ↔ kameralarni moslashtirish (connect/disconnect)
core/EventBuffer.h         — jonli eventlar (xotirada)
db/Database.*              — SQLite (groups, cameras, settings, connection_log)
web/WebServer.*            — QHttpServer REST API + panel
web/index.html             — web panel (SPA), web.qrc orqali binarига embed
docker/                    — Dockerfile, build.sh
```

---

## 11. To'xtatish / qayta ishga tushirish

```bash
# Native
pkill -f 'Projects/Qt/DRB/build/Server'
./build/Server --db data.db --http-port 8080 --user admin --password PAROL

# Docker
docker stop camera-server && docker start camera-server
```

---

## 12. Muammolarni hal qilish

| Belgi | Sabab / yechim |
|-------|----------------|
| Login bo'lmayapti | Parol noto'g'ri. Default `admin/admin` (agar boshqasi berilmagan bo'lsa). |
| Kamera 🔴 uzilgan | IP/port/login tekshiring; kamera serverdan tarmoqda yetib borishini tekshiring. |
| Event kelmayapti | Kamera ulangan (🟢) bo'lishi va ANPR (raqam tanish) yoqilgan bo'lishi kerak. |
| Reconnect soni oshib boryapti | Tarmoq beqaror yoki kamera uzilib turibdi. |
| Guruh URL'iga bormayapti | Guruh `post_url` to'g'riligini va server javob berishini tekshiring. |
| Port band | Boshqa `--http-port` bering. |
