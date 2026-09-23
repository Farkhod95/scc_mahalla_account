"""
Papkadagi BARCHA mahalla passportlarini bitta buyruq bilan yuklaydi.

    python manage.py import_mahalla_folder files/
    python manage.py import_mahalla_folder files/ --dry-run
    python manage.py import_mahalla_folder files/ --only charxnovza,gulobod

Har bir fayl uchun alohida buyruq yozish shart emas — mahalla fayl
NOMIDAN aniqlanadi (`MAHALLA_KEYWORDS`).

Nima uchun nomdan: varaq sarlavhasiga ishonib bo'lmaydi. Ba'zi fayllar
boshqa mahallaning shablonidan ko'chirilgan va sarlavha yangilanmagan
(masalan "Kamolon Darvoza MFY Malumot yangi.xlsx" ichidagi ba'zi
qatorlarda inspektorning boshqa MFY dagi manzili turadi). Shu sabab
sarlavha faqat TEKSHIRUV uchun ishlatiladi — mos kelmasa ogohlantirish
chiqadi, import to'xtamaydi.

Bitta fayl xato bersa qolganlari davom etadi; oxirida umumiy hisobot.
"""
import re
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from directory.models import Mahalla

# Fayl nomidagi kalit so'z -> mahalla kodi.
# Kalitlar lotinlashtirilgan va normalizatsiya qilingan ko'rinishda
# (faqat kichik harf va raqam). Bir necha kalit mos kelsa ENG UZUNI olinadi —
# shu sabab "obod" "nurliobod" ni buzmaydi.
#
# Kodlar — `Mahalla.code`, ya'ni {tuman SOATO}{tartib:03d}. Shayxontohur
# tumani SOATO si 1726277: 1-Gom mahallalari 001—012, bazada avvaldan
# turgan 2-Gom va 3-Gom mahallalari esa 013—024.
# Yangi passport fayllari kelganda shu jadval to'ldiriladi.
MAHALLA_KEYWORDS = {
    "charxnovza": "1726277001",
    "eshonguzar": "1726277002",
    "gulobod": "1726277003",
    # "Камолон" fayli — "kamolon" yolg'iz uchta faylga (Камолон, Камолон
    # Дарвоза, Янги Камолон) mos kelgani uchun uzunroq kalit olindi.
    "kamolonmfyxlsx": "1726277004",
    "kamolondarvoza": "1726277005",
    "kattaoqtepa": "1726277006",
    "kattabog": "1726277007",
    "olimxojayev": "1726277008",
    "sdarvoza": "1726277009",
    # "CУЗУКОТА …" — fayl nomi lotin "C" bilan boshlanadi (kirill "С" emas),
    # shuning uchun kalit "suzukota" emas, "cuzukota".
    "cuzukota": "1726277010",
    "yangikamolon": "1726277011",
    "zangiota": "1726277012",
}


def norm(value):
    """Taqqoslash uchun: lotinga o'girib, faqat harf va raqam qoldiradi."""
    from restapp.utils.translit import to_latin
    return re.sub(r"[^0-9a-z]", "", to_latin(str(value)).lower())


def guess_code(filename):
    """Fayl nomidan mahalla kodini topadi -> (kod, kalit) yoki (None, None)."""
    text = norm(Path(filename).stem)
    hits = [(k, c) for k, c in MAHALLA_KEYWORDS.items() if k in text]
    if not hits:
        return None, None
    key, code = max(hits, key=lambda h: len(h[0]))
    return code, key


class Command(BaseCommand):
    help = "Papkadagi barcha mahalla passport fayllarini yuklaydi."

    def add_arguments(self, parser):
        parser.add_argument("folder", nargs="?", default="files",
                            help="Passport fayllari turgan papka (default: files)")
        parser.add_argument("--dry-run", action="store_true",
                            help="Bazaga yozmaydi, faqat nima bo'lishini ko'rsatadi")
        parser.add_argument("--no-photos", action="store_true",
                            help="Rasmlarni yuklamaydi")
        parser.add_argument("--only", default="",
                            help="Faqat shu kalit so'zli fayllar, vergul bilan "
                                 "(masalan: charxnovza,gulobod)")
        parser.add_argument("--list", action="store_true",
                            help="Import qilmaydi, faqat fayl -> mahalla jadvalini "
                                 "ko'rsatadi")

    def handle(self, *args, **options):
        folder = Path(options["folder"])
        if not folder.is_dir():
            raise CommandError(f"Papka topilmadi: {folder}")

        files = sorted(p for p in folder.glob("*.xlsx") if not p.name.startswith("~$"))
        if not files:
            raise CommandError(f"{folder} da .xlsx fayl yo'q")

        only = [o.strip().lower() for o in options["only"].split(",") if o.strip()]

        # ---------------------------------------------------- moslikni tuzish
        plan, unknown = [], []
        for path in files:
            code, key = guess_code(path.name)
            if code is None:
                unknown.append(path)
                continue
            if only and not any(o in norm(path.name) or o == key for o in only):
                continue
            plan.append((path, code, key))

        # Bir mahallaga bir nechta fayl tushib qolmasin
        by_code = {}
        for path, code, key in plan:
            by_code.setdefault(code, []).append(path)
        duplicates = {c: p for c, p in by_code.items() if len(p) > 1}

        names = {m.code: m for m in Mahalla.objects.filter(
            code__in=[c for _, c, _ in plan])}

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n{folder} — {len(files)} fayl, {len(plan)} tasi biriktirildi\n"))
        for path, code, key in plan:
            mahalla = names.get(code)
            label = mahalla.name_uz if mahalla else "BAZADA YO'Q"
            size = path.stat().st_size / 1e6
            self.stdout.write(f"  {path.name[:44]:46} {size:6.0f} MB  ->  "
                              f"{code}  {label}")
        for path in unknown:
            self.stdout.write(self.style.WARNING(
                f"  {path.name[:44]:46}          ANIQLANMADI — o'tkazib yuborildi"))
        for code, paths in duplicates.items():
            self.stdout.write(self.style.ERROR(
                f"  DIQQAT: {code} ga {len(paths)} ta fayl mos keldi: "
                f"{', '.join(p.name for p in paths)}"))

        missing = [c for _, c, _ in plan if c not in names]
        if missing:
            raise CommandError(f"Bazada yo'q mahalla kodlari: {', '.join(missing)}")

        if options["list"]:
            return

        # ------------------------------------------------------------- import
        ok, failed = [], []
        for i, (path, code, key) in enumerate(plan, 1):
            line = "=" * 70
            self.stdout.write(self.style.MIGRATE_HEADING(
                f"\n{line}\n[{i}/{len(plan)}] {path.name}  ->  "
                f"{names[code].name_uz} ({code})\n{line}"))
            try:
                call_command("import_mahalla_data", str(path),
                             mahalla_code=code,
                             dry_run=options["dry_run"],
                             no_photos=options["no_photos"])
                ok.append(path.name)
            except Exception as exc:
                failed.append((path.name, f"{type(exc).__name__}: {exc}"))
                self.stdout.write(self.style.ERROR(f"XATO: {exc}"))

        # ----------------------------------------------------------- hisobot
        line = "=" * 70
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n{line}\nYAKUNIY HISOBOT\n{line}"))
        self.stdout.write(self.style.SUCCESS(f"muvaffaqiyatli: {len(ok)}"))
        if failed:
            self.stdout.write(self.style.ERROR(f"xato: {len(failed)}"))
            for name, err in failed:
                self.stdout.write(self.style.ERROR(f"  {name}: {err}"))
        if options["dry_run"]:
            self.stdout.write(self.style.WARNING(
                "\nDRY-RUN edi — bazaga hech narsa yozilmadi"))
