import os
from collections import OrderedDict

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from openpyxl import load_workbook

from monitoring.models import Shop, ShopTenant, TenantEmployee
from monitoring.tasks import (
    empty_or_zero_to_none,
    normalize_block_type,
    normalize_business_type,
    normalize_fire_safety_level,
    normalize_activity_status,
    normalize_jshshir,
    normalize_phone,
    normalize_shop_number,
    normalize_tax_type,
    parse_decimal,
    parse_int,
    split_employee_phones,
    split_multiline,
)

DEFAULT_FILE = os.path.join("docs", "МАЛИКА АДМИНСТРАЦИЯГА.xlsx")

# Sheet 2 (index 1) ustun tartib raqamlari (0-dan boshlanadi)
COL_BLOCK = 1
COL_SHOP_NUM = 2
COL_OWNER_FIO = 3
COL_OWNER_JSHSHIR = 4
COL_OWNER_PHONE = 5
COL_OWNER_COMPANY = 6
COL_TOTAL_AREA = 7
COL_TENANTS_COUNT = 8
COL_RENTED_AREA = 9
COL_TENANT_NAME = 10
COL_LEADER_JSHSHIR = 11
COL_LEADER_FIO = 12
COL_LEADER_PHONE = 13
COL_YTT_JSHSHIR = 14
COL_STIR = 15
COL_EMP_COUNT = 16
COL_EMP_FIO = 17
COL_EMP_JSHSHIR = 18
COL_EMP_PHONE = 19
COL_BUSINESS_TYPE = 20
COL_TAX_TYPE = 21
COL_CASH_REG = 22
COL_ACTIVITY = 23
COL_FIRE_SAFETY = 24


def _trunc(value, max_len):
    if value is None:
        return None
    return str(value)[:max_len]


def _get(row, col):
    if col >= len(row):
        return None
    return row[col]


class Command(BaseCommand):
    help = (
        "docs/МАЛИКА АДМИНСТРАЦИЯГА.xlsx faylidan do'kon, ijrachi va "
        "xodimlarni import qiladi. Bir do'konda egasi almashgan bo'lsa "
        "oxirgi qator ma'lumoti olinadi."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default=None,
            help=f"Excel fayl yo'li (default: {DEFAULT_FILE})",
        )
        parser.add_argument(
            "--sheet",
            default=1,
            type=int,
            help="Excel sheet indeksi 0-dan (default: 1 — ikkinchi sheet)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Ma'lumotlar bazasiga yozmasdan natijani ko'rsatadi",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        if not file_path:
            file_path = os.path.join(settings.BASE_DIR, DEFAULT_FILE)

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"Fayl topilmadi: {file_path}"))
            return

        sheet_index = options["sheet"]
        dry_run = options["dry_run"]

        wb = load_workbook(file_path, data_only=True)
        sheet_names = wb.sheetnames

        if sheet_index >= len(sheet_names):
            self.stderr.write(
                self.style.ERROR(
                    f"Sheet {sheet_index} topilmadi. Mavjud: {sheet_names}"
                )
            )
            return

        ws = wb[sheet_names[sheet_index]]
        self.stdout.write(
            f"Fayl: {file_path}\n"
            f"Sheet: [{sheet_index}] {sheet_names[sheet_index]} "
            f"({ws.max_row} qator x {ws.max_column} ustun)"
        )

        # 1-pass: barcha qatorlarni yig'ib (block_type, shop_number) bo'yicha guruhlash
        shop_rows: OrderedDict = OrderedDict()
        skipped_rows = 0

        for row in ws.iter_rows(min_row=2, values_only=True):
            # bo'sh qatorlar va header qatori o'tkaziladi
            raw_num = _get(row, 0)
            if raw_num is None:
                continue
            try:
                int(raw_num)
            except (TypeError, ValueError):
                continue

            block_type = normalize_block_type(_get(row, COL_BLOCK))
            shop_number = normalize_shop_number(_get(row, COL_SHOP_NUM))

            if not block_type or not shop_number:
                skipped_rows += 1
                continue

            key = (block_type, shop_number)
            if key not in shop_rows:
                shop_rows[key] = []
            shop_rows[key].append(row)

        self.stdout.write(
            f"\n{len(shop_rows)} ta noyob do'kon topildi. "
            f"{skipped_rows} qator blok/raqam yo'qligi sababli o'tkazildi."
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("--- DRY RUN rejimi ---"))

        created_shops = 0
        updated_shops = 0
        created_tenants = 0
        updated_tenants = 0
        created_employees = 0
        error_list = []

        # 2-pass: har bir do'kon uchun oxirgi qator egasi, barcha tenant qatorlari
        for (block_type, shop_number), rows in shop_rows.items():
            try:
                with transaction.atomic():
                    # Egasi: oxirgi bo'sh bo'lmagan qator (egasi almashgan holat)
                    # Bo'sh qatorlar o'tkaziladi, almashgan bo'lsa yangi egasi olinadi
                    owner_fio = None
                    owner_jshshir = None
                    owner_phone = None
                    owner_company = None
                    for row in reversed(rows):
                        candidate = empty_or_zero_to_none(_get(row, COL_OWNER_FIO))
                        if candidate:
                            owner_fio = _trunc(candidate, 255)
                            owner_jshshir = _trunc(
                                normalize_jshshir(_get(row, COL_OWNER_JSHSHIR)), 255
                            )
                            owner_phone = _trunc(
                                normalize_phone(_get(row, COL_OWNER_PHONE)), 255
                            )
                            owner_company = _trunc(
                                empty_or_zero_to_none(_get(row, COL_OWNER_COMPANY)), 255
                            )
                            break

                    # Umumiy maydon: birinchi noldan farqli qiymat
                    total_area = None
                    for row in rows:
                        area = parse_decimal(_get(row, COL_TOTAL_AREA))
                        if area and area > 0:
                            total_area = area
                            break

                    shop_data = {
                        "owner_fio": owner_fio,
                        "owner_jshshir": owner_jshshir,
                        "owner_phone": owner_phone,
                        "owner_company_name": owner_company,
                        "total_area": total_area,
                        "tenants_count": len(rows),
                    }

                    if not dry_run:
                        shop, shop_created = Shop.objects.update_or_create(
                            block_type=block_type,
                            shop_number=shop_number,
                            defaults=shop_data,
                        )
                        if shop_created:
                            created_shops += 1
                        else:
                            updated_shops += 1
                    else:
                        shop = None
                        created_shops += 1

                    # Har bir tenant qatori
                    for row in rows:
                        tenant_name = _trunc(
                            empty_or_zero_to_none(_get(row, COL_TENANT_NAME)), 255
                        )
                        leader_jshshir = normalize_jshshir(_get(row, COL_LEADER_JSHSHIR))
                        if not leader_jshshir:
                            # YTT bo'lsa col 14 dan olish
                            leader_jshshir = normalize_jshshir(_get(row, COL_YTT_JSHSHIR))
                        leader_jshshir = _trunc(leader_jshshir, 255)

                        leader_fio = _trunc(
                            empty_or_zero_to_none(_get(row, COL_LEADER_FIO)), 255
                        )
                        leader_phone = _trunc(
                            normalize_phone(_get(row, COL_LEADER_PHONE)), 255
                        )

                        stir = normalize_jshshir(_get(row, COL_STIR))
                        stir = _trunc(stir, 30)

                        if not tenant_name and not leader_fio and not leader_jshshir:
                            continue

                        tax_type = normalize_tax_type(_get(row, COL_TAX_TYPE))
                        is_vat = tax_type == ShopTenant.TaxType.VAT

                        cash_reg = _trunc(
                            empty_or_zero_to_none(_get(row, COL_CASH_REG)), 80
                        )

                        tenant_data = {
                            "name": tenant_name,
                            "leader_fio": leader_fio,
                            "leader_jshshir": leader_jshshir,
                            "leader_phone": leader_phone,
                            "stir": stir,
                            "certificate_number": None,
                            "rented_area": parse_decimal(_get(row, COL_RENTED_AREA)),
                            "business_type": normalize_business_type(
                                _get(row, COL_BUSINESS_TYPE)
                            ),
                            "tax_type": tax_type,
                            "activity_status": normalize_activity_status(
                                _get(row, COL_ACTIVITY)
                            ),
                            "employees_count": parse_int(_get(row, COL_EMP_COUNT)),
                            "cash_register_number_vat": cash_reg if is_vat else None,
                            "cash_register_number_turnover": None if is_vat else cash_reg,
                            "fire_safety_level": normalize_fire_safety_level(
                                _get(row, COL_FIRE_SAFETY)
                            ),
                        }

                        if not dry_run:
                            # Mavjud tenant izlash
                            tenant = None
                            if leader_jshshir:
                                tenant = ShopTenant.objects.filter(
                                    shop=shop, leader_jshshir=leader_jshshir
                                ).first()
                            if not tenant and tenant_name:
                                tenant = ShopTenant.objects.filter(
                                    shop=shop, name=tenant_name
                                ).first()

                            if tenant:
                                for field, val in tenant_data.items():
                                    setattr(tenant, field, val)
                                tenant.save()
                                updated_tenants += 1
                            else:
                                tenant = ShopTenant.objects.create(
                                    shop=shop, **tenant_data
                                )
                                created_tenants += 1

                            # Xodimlar
                            emp_fios = split_multiline(_get(row, COL_EMP_FIO))
                            emp_jshshirs = split_multiline(_get(row, COL_EMP_JSHSHIR))
                            emp_phones = split_employee_phones(_get(row, COL_EMP_PHONE))

                            tenant.employees.all().delete()

                            max_emp = max(
                                len(emp_fios), len(emp_jshshirs), len(emp_phones)
                            )
                            for i in range(max_emp):
                                fio = _trunc(
                                    empty_or_zero_to_none(
                                        emp_fios[i] if i < len(emp_fios) else None
                                    ),
                                    255,
                                )
                                jshshir = _trunc(
                                    normalize_jshshir(
                                        emp_jshshirs[i] if i < len(emp_jshshirs) else None
                                    ),
                                    20,
                                )
                                phone = _trunc(
                                    normalize_phone(
                                        emp_phones[i] if i < len(emp_phones) else None
                                    ),
                                    30,
                                )

                                if not fio and not jshshir and not phone:
                                    continue

                                TenantEmployee.objects.create(
                                    tenant=tenant,
                                    fio=fio,
                                    jshshir=jshshir,
                                    phone=phone,
                                )
                                created_employees += 1
                        else:
                            created_tenants += 1

            except Exception as exc:
                label = f"Blok {block_type} - {shop_number}-do'kon"
                error_list.append(f"{label}: {exc}")
                self.stderr.write(self.style.WARNING(f"Xato [{label}]: {exc}"))

        prefix = "(DRY RUN) " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{prefix}Import yakunlandi:\n"
                f"  Do'konlar  : {created_shops} yangi, {updated_shops} yangilandi\n"
                f"  Ijarachilar: {created_tenants} yangi, {updated_tenants} yangilandi\n"
                f"  Xodimlar   : {created_employees} yangi\n"
                f"  Xatolar    : {len(error_list)} ta"
            )
        )

        if error_list:
            self.stdout.write("\nXatolar ro'yxati:")
            for err in error_list:
                self.stdout.write(f"  - {err}")
