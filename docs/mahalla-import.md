# Mahalla passportini bazaga yuklash

Shayxontohur tumani **1-sonli IIB (GOM)** va unga qaraydigan 12 ta MFY
passporti uchun yozilgan. Xuddi shu buyruqlar keyingi GOM/MFY lar uchun ham
ishlaydi — faqat jadvallarni to'ldirish kerak.

## Buyruqlar

| Buyruq | Nima qiladi |
|--------|-------------|
| `directory/management/commands/import_gom.py` | GOM va uning mahallalarini (bo'sh yozuv) yaratadi |
| `monitoring/management/commands/import_mahalla_data.py` | BITTA passport faylini o'qib bazaga yozadi |
| `monitoring/management/commands/import_mahalla_folder.py` | Papkadagi hamma passportni fayl nomi bo'yicha mahallaga biriktirib yuklaydi |

Passport fayllari `files/` da turadi va **git ga tushmaydi** (yuzlab MB).
Import serverda yurgiziladi — rasmlar `MEDIA_ROOT` ga, ya'ni `media_volume`
docker hajmiga yozilishi kerak.

## Tartib

Fayllarni serverdagi repo papkasining `files/` iga ko'chirib oling
(`docker-compose.yml` da `.:/app` bind-mount qilingan, shuning uchun ular
konteyner ichida `/app/files/` bo'lib ko'rinadi).

```bash
# 1. GOM va 12 ta mahalla (avval quruq yurgizib ko'ring)
docker exec mahalla_account_web python manage.py import_gom --dry-run
docker exec mahalla_account_web python manage.py import_gom

# 2. Qaysi fayl qaysi mahallaga tushishini tekshirish (bazaga tegmaydi)
docker exec mahalla_account_web python manage.py import_mahalla_folder files/ --list

# 3. Import
docker exec mahalla_account_web python manage.py import_mahalla_folder files/ --dry-run
docker exec mahalla_account_web python manage.py import_mahalla_folder files/
```

Foydali bayroqlar:

* `--only charxnovza,gulobod` — faqat shu fayllar. 70 MB lik fayllar openpyxl
  da ancha xotira oladi; konteyner xotiraga tiqilsa fayllarni shu bayroq bilan
  bittalab yuklang.
* `--no-photos` — rasmlarsiz (tezroq; matnni qayta yuklash uchun).

Hammasi **idempotent**: qayta yurgizilsa yozuvlar takrorlanmaydi, mavjudlari
yangilanadi. `import_gom` mavjud GOM/mahallaga umuman tegmaydi, faqat bo'sh
maydonlarini to'ldiradi.

## Nima qayerga tushadi

| Excel varag'i | Model |
|---------------|-------|
| `умумий` — faollar bloki | `Employee` (+ kerak bo'lsa `Position`) |
| `умумий` — sonlar bloki | `MahallaInformation` (+ `MahallaInformationCategory`) |
| `умумий` — obyektlar bloki | `Object` (`ObjectCategory` bo'yicha) |
| `рухий касаллар` | `MFYCitizen` `category=ruhiy` |
| `наркоманлар` | `MFYCitizen` `category=narko` |
| `жанжалкаш оилалар` | `MFYCitizen` `category=janjal` |
| `содир этилган жиноят` | `MahallaCrime` (+ `CrimeCategory`) |
| `ОЧ`, `АТИ` | mos model yo'q — o'tkazib yuboriladi |

Obyektlarning o'zi `умумий` dan olinadi (u yerda tashkilot nomi ham bor),
rasmlari esa alohida varaqlardan rahbar F.I.Sh bo'yicha topib qo'shiladi.
Matn kirilldan lotinga o'giriladi (`restapp/utils/translit.py`).

## Ogohlantirishlarni o'qish

Har bir fayldan keyin ogohlantirishlar ro'yxati chiqadi. Ko'pi axborot uchun
(rasm kesildi, koordinata tiklandi). Qo'l bilan tekshirish kerak bo'lganlari:

* **`turkum tanilmadi ('…')`** — `умумий` dagi turkum nomi
  `OBJECT_CATEGORY_KEY` da yo'q, **obyekt qo'shilmadi**. Turkum bazada bo'lsa
  shu jadvalga qator qo'shing va faylni qayta yuklang.
* **`YANGI lavozim yaratildi`** / **`YANGI ko'rsatkich turkumi yaratildi`** —
  bazada mos yozuv topilmadi. Bu imlo varianti bo'lsa `POSITION_ALIASES` yoki
  `INFO_CATEGORY_ALIASES` ga alias qo'shing, aks holda yangi turkum bazada
  dublikat bo'lib qoladi.
* **`tasnif ustunida turkum emas, voqea bayoni yozilgan`** — jinoyat
  varag'ining tasnif ustuniga butun voqea matni yozilgan. Jinoyatning o'zi
  saqlanadi, turkumi bo'sh qoladi — admin paneldan qo'yiladi.
* **`sarlavhadagi mahalla mos emas`** — fayl boshqa mahallanikidan ko'chirilgan
  bo'lishi mumkin. `--list` chiqishi bilan solishtiring.

## 1-Gom natijasi

12 ta faylning hammasi muvaffaqiyatli o'qildi (lokal nusxada tekshirilgan):

| Mahalla | Obyekt | Xodim | Fuqaro | Jinoyat | Ko'rsatkich | Rasm |
|---------|-------:|------:|-------:|--------:|------------:|-----:|
| Charxnovza | 25 | 6 | 12 | 2 | 6 | 31 |
| Eshonguzar | 71 | 3 | 23 | 5 | 6 | 31 |
| Gulobod | 24 | 3 | 19 | 0 | 7 | 24 |
| Kamolon | 49 | 2 | 9 | 2 | 6 | 45 |
| Kamolon Darvoza | 63 | 3 | 28 | 1 | 6 | 51 |
| Katta Oqtepa | 46 | 3 | 50 | 3 | 6 | 87 |
| Kattabogʻ | 74 | 2 | 22 | 4 | 6 | 29 |
| Olim Xoʻjayev | 53 | 3 | 9 | 2 | 6 | 60 |
| Samarqand Darvoza | 42 | 3 | 31 | 5 | 6 | 70 |
| Suzukota | 14 | 2 | 23 | 3 | 6 | 29 |
| Yangi Kamolon | 27 | 3 | 14 | 0 | 6 | 39 |
| Zangiota | 116 | 3 | 9 | 4 | 5 | 16 |
| **Jami** | **604** | **36** | **249** | **31** | **72** | **512** |

Qo'shimcha yaratiladigan ma'lumotnoma yozuvlari:

* `Position`: `Xokim yordamchisi`, `Yoshlar yetakchisi`, `Ijtimoiy xodim`
* `MahallaInformationCategory`: `Ayollar soni`, `Erkaklar soni`, `Yoshlar soni`
* `CrimeCategory`: `Firibgarlik`, `Tovlamachilik`, `Qasddan odam oʻldirish`,
  `Giyoxvandlik`, `Qoʻshmachilik`, `Foxisha xona tashkil qilish`,
  `Skuter o'g'irlanganligi`, `oilaviy zoʻravonlik`

Bazada turkumi yo'qligi uchun **6 ta obyekt** qo'shilmadi — `Нонвой хона` (2),
`Спорт мактаби`, `Автомобилларга хизмат кўрсатиш`, `Ichimliq suv markazi`,
`tumani elektr tarmoqlari`. Kerak bo'lsa avval `ObjectCategory` qo'shib,
keyin `OBJECT_CATEGORY_KEY` ga mos qator yozing.
