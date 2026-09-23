"""
Shayxontohur tumani 1-sonli IIB (GOM) va unga qaraydigan 12 ta MFY.

    python manage.py import_gom
    python manage.py import_gom --dry-run
    python manage.py import_gom --gom-code 100100

Bazada 2-Gom (kod 100230) va 3-Gom (kod 100110) hamda ularning 12 ta
mahallasi (kodlar 1726277013—024) avvaldan bor edi. Bu buyruq 1-Gom ni va
kodlari 1726277001—012 bo'lgan 12 ta mahallani qo'shadi — passport
ma'lumotini keyin `import_mahalla_folder` yuklaydi.

Mahalla kodi = {tuman SOATO}{tartib:03d}. Shayxontohur SOATO si 1726277,
tartib raqami lotin nomi bo'yicha alifbo tartibida berilgan.

Buyruq IDEMPOTENT: takroran yurgizilsa yangi yozuv yaratilmaydi. Mahalla
avval kodi bo'yicha, topilmasa nomi bo'yicha qidiriladi (qo'lda kiritilgan
bo'lishi mumkin) — topilgan yozuvning faqat BO'SH maydonlari va `gom`
biriktirmasi to'ldiriladi, to'ldirilgan maydonlarga tegilmaydi.
"""
import re

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from directory.models import District, Gom, Mahalla
from restapp.utils.translit import to_latin

DISTRICT_CODE = "1726277"          # Shayxontohur tumani (SOATO)
GOM_NAME = "1-Gom"                 # mavjud yozuvlar uslubi: '2-Gom', '3-Gom'

# (Mahalla.code, lotin nomi, kirill nomi)
#
# Kirill nomlari passport fayllarining sarlavhasidan olingan
# (`Шайхонтохур тумани "…" М.Ф.Й фаоллари тўғрисида маълумотнома`) —
# `name_ru` shunga yoziladi, bazadagi mavjud yozuvlardagi kabi.
MAHALLAS = (
    ("1726277001", "Charxnovza", "Чархновза"),
    ("1726277002", "Eshonguzar", "Эшонгузар"),
    ("1726277003", "Gulobod", "Гулобод"),
    ("1726277004", "Kamolon", "Камолон"),
    ("1726277005", "Kamolon Darvoza", "Камолон Дарвоза"),
    ("1726277006", "Katta Oqtepa", "Катта Оқтепа"),
    ("1726277007", "Kattabogʻ", "Каттабоғ"),
    ("1726277008", "Olim Xoʻjayev", "Олим Хўжайев"),
    ("1726277009", "Samarqand Darvoza", "Самарқанд Дарвоза"),
    ("1726277010", "Suzukota", "Сузукота"),
    ("1726277011", "Yangi Kamolon", "Янги Камолон"),
    ("1726277012", "Zangiota", "Зангиота"),
)


def ascii_name(value):
    """`name_en` uchun: ʻ/ʼ tushiriladi — bazadagi uslub (Oʻqchi -> Oqchi)."""
    return value.replace("ʻ", "").replace("ʼ", "").replace("'", "")


def fold(value):
    """
    Nomlarni solishtirish kaliti.

    Faqat harf va raqam qoldiriladi, `MFY` olib tashlanadi, `h` va `x`
    birlashtiriladi ("Xo'jayev" ~ "Hojayev"), `ʻ` tushiriladi
    ("Kattabogʻ" ~ "Kattabog").
    """
    text = to_latin(str(value or "")).lower()
    text = re.sub(r"\bm\.?\s*f\.?\s*y\.?\b", " ", text)
    text = re.sub(r"[^0-9a-z]", "", text)
    return text.replace("h", "x")


class Command(BaseCommand):
    help = "Shayxontohur 1-Gom va uning 12 ta mahallasini bazaga qo'shadi."

    def add_arguments(self, parser):
        parser.add_argument("--district-code", default=DISTRICT_CODE,
                            help=f"Tuman kodi (default: {DISTRICT_CODE} — Shayxontohur)")
        parser.add_argument("--gom-name", default=GOM_NAME,
                            help=f"GOM nomi (default: {GOM_NAME})")
        parser.add_argument("--gom-code", default=None,
                            help="GOM kodi. Berilmasa bo'sh qoladi — haqiqiy IIB "
                                 "kodi ma'lum bo'lganda admin paneldan kiritiladi.")
        parser.add_argument("--dry-run", action="store_true",
                            help="Bazaga yozmaydi, faqat nima bo'lishini ko'rsatadi")

    # -------------------------------------------------------------------- gom
    def resolve_gom(self, name, code, district):
        """
        `name` bo'yicha GOM ni topadi, bo'lmasa yaratadi.

        Mavjud yozuv HECH QACHON o'zgartirilmaydi — kodi yoki hududi qo'lda
        to'g'rilangan bo'lishi mumkin.
        """
        gom = Gom.objects.filter(district=district, name=name).order_by("id").first()
        if gom:
            return gom, "mavjud"

        if self.dry:
            return None, "YARATILADI"

        gom = Gom.objects.create(
            code=code, name=name, name_uz=name, name_ru=name, name_en=name,
            region=district.region, district=district, is_active=True)
        return gom, "yaratildi"

    # ---------------------------------------------------------------- mahalla
    def resolve_mahalla(self, code, name, district, by_name):
        """
        Mavjud mahallani qaytaradi: avval kod bo'yicha, keyin nom bo'yicha.

        Nom bo'yicha topilishi — mahalla avval qo'lda, boshqa kod bilan
        kiritilgan holat. Bunda kodga TEGILMAYDI, faqat ogohlantiriladi:
        kodni almashtirish `import_mahalla_folder` dagi biriktirmani buzadi.
        """
        found = Mahalla.objects.filter(district=district, code=code).first()
        if found:
            return found, None

        matches = by_name.get(fold(name), [])
        if len(matches) == 1:
            found = matches[0]
            return found, (f"{name}: kodi {code} emas, {found.code!r} — mavjud "
                           f"yozuv (id={found.pk}) ishlatildi, kod o'zgartirilmadi")
        if matches:
            return None, (f"{name}: bir xil nomli {len(matches)} ta mahalla bor — "
                          f"o'tkazib yuborildi")
        return None, None

    def apply_fields(self, mahalla, code, name, name_cyr, district, gom):
        """Faqat BO'SH maydonlarni to'ldiradi. Nimalar o'zgargani qaytariladi."""
        wanted = {
            "code": code,
            "name": name,
            "name_uz": name,
            "name_ru": name_cyr,
            "name_en": ascii_name(name),
            "region": district.region,
            "district": district,
            "gom": gom,
        }
        changed = []
        for field, value in wanted.items():
            if value is None:
                continue
            if not getattr(mahalla, field, None):
                setattr(mahalla, field, value)
                changed.append(field)
        return changed

    # ----------------------------------------------------------------- handle
    def handle(self, *args, **options):
        self.dry = options["dry_run"]

        district = District.objects.select_related("region").filter(
            code=options["district_code"]).first()
        if not district:
            raise CommandError(f"tuman topilmadi: code={options['district_code']}")

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n{district.name} (id={district.pk}, code={district.code})"))
        if self.dry:
            self.stdout.write(self.style.WARNING("DRY-RUN: bazaga yozilmaydi\n"))

        warnings = []
        created = updated = untouched = 0

        with transaction.atomic():
            gom, note = self.resolve_gom(
                options["gom_name"], options["gom_code"], district)
            self.stdout.write(f"GOM {options['gom_name']}: {note}"
                              + (f" (id={gom.pk})" if gom else ""))

            by_name = {}
            for m in Mahalla.objects.filter(district=district):
                by_name.setdefault(fold(m.name_uz or m.name), []).append(m)

            for code, name, name_cyr in MAHALLAS:
                mahalla, warn = self.resolve_mahalla(code, name, district, by_name)
                if warn:
                    warnings.append(warn)
                if mahalla is None and warn:      # nomi bir xil bir nechta yozuv
                    continue

                if mahalla is None:
                    if self.dry:
                        self.stdout.write(f"  {code}  {name:20} YARATILADI")
                        created += 1
                        continue
                    mahalla = Mahalla(
                        code=code, name=name, name_uz=name, name_ru=name_cyr,
                        name_en=ascii_name(name), region=district.region,
                        district=district, gom=gom, is_active=True)
                    mahalla.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"  {code}  {name:20} yaratildi (id={mahalla.pk})"))
                    created += 1
                    continue

                changed = self.apply_fields(
                    mahalla, code, name, name_cyr, district, gom)
                if changed and not self.dry:
                    mahalla.save()
                if changed:
                    self.stdout.write(
                        f"  {mahalla.code}  {name:20} to'ldirildi: {', '.join(changed)}")
                    updated += 1
                else:
                    self.stdout.write(f"  {mahalla.code}  {name:20} o'zgarishsiz")
                    untouched += 1

            if self.dry:
                transaction.set_rollback(True)

        self.stdout.write(self.style.MIGRATE_HEADING("\nHISOBOT"))
        self.stdout.write(f"  yangi mahalla   : {created}")
        self.stdout.write(f"  to'ldirildi     : {updated}")
        self.stdout.write(f"  o'zgarishsiz    : {untouched}")
        for w in warnings:
            self.stdout.write(self.style.WARNING(f"  ! {w}"))
        if self.dry:
            self.stdout.write(self.style.WARNING(
                "\nDRY-RUN edi — bazaga hech narsa yozilmadi"))
