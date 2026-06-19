"""
Savdo tushumlari (faktura + OKKM) — tashkilotlar bo'yicha OYLIK Excel hisobot.

Har bir tashkilot (ShopTenant, STIR bo'yicha) qator, har oy (Yan..Dek) ustun.
Qiymat = FacturaRevenueDaily.sales + OkkmRevenueDaily.turnover (xom so'm), shu
oyda yig'ilgan. Bu dashboarddagi "Savdo tushumlari" bilan bir xil manba.

GET /api/v1/reports/sales-revenue/excel?year=2026
  ?year= berilmasa — joriy yil.
"""
import io
from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from monitoring.models import FacturaRevenueDaily, OkkmRevenueDaily, ShopTenant

MONTHS_UZ = [
    "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
    "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr",
]

XLSX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


class SalesRevenueExcelView(APIView):
    """Tashkilotlar bo'yicha oylik savdo tushumlari (faktura + OKKM) — .xlsx."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            year = int(request.query_params.get("year") or date.today().year)
        except (TypeError, ValueError):
            year = date.today().year

        # 1) Faktura va OKKM ni tin x oy bo'yicha DB da yig'amiz, keyin birlashtiramiz.
        #    revenue[tin][month_index 0..11] = Decimal savdo
        revenue: dict[str, list[Decimal]] = defaultdict(
            lambda: [Decimal(0)] * 12
        )

        for r in (
            FacturaRevenueDaily.objects
            .filter(date__year=year)
            .values("seller_tin", "date__month")
            .annotate(s=Sum("sales"))
        ):
            tin = (r["seller_tin"] or "").strip()
            if tin:
                revenue[tin][r["date__month"] - 1] += r["s"] or Decimal(0)

        for r in (
            OkkmRevenueDaily.objects
            .filter(date__year=year)
            .values("tin", "date__month")
            .annotate(o=Sum("turnover"))
        ):
            tin = (r["tin"] or "").strip()
            if tin:
                revenue[tin][r["date__month"] - 1] += r["o"] or Decimal(0)

        # 2) STIR -> tashkilot nomi + do'kon(lar). Bitta STIR bir nechta do'konda
        #    bo'lishi mumkin — nomlarni va do'konlarni birlashtiramiz.
        info_by_stir: dict[str, dict] = {}
        for t in (
            ShopTenant.objects
            .exclude(stir__isnull=True).exclude(stir="")
            .select_related("shop")
        ):
            stir = (t.stir or "").strip()
            if not stir:
                continue
            entry = info_by_stir.setdefault(stir, {"name": None, "shops": []})
            if not entry["name"]:
                entry["name"] = (t.name or t.leader_fio or "").strip() or None
            if t.shop_id:
                label = str(t.shop)
                if label not in entry["shops"]:
                    entry["shops"].append(label)

        # 3) Qatorlar: jami bo'yicha kamayish tartibida (eng katta tashkilot tepada).
        rows = []
        for tin, months in revenue.items():
            total = sum(months, Decimal(0))
            if total == 0:
                continue  # shu yilda savdosi bo'lmagan tin lar tushmasin
            info = info_by_stir.get(tin)
            name = (info["name"] if info and info["name"] else tin)
            shop = ", ".join(info["shops"]) if info and info["shops"] else ""
            rows.append({
                "name": name,
                "stir": tin,
                "shop": shop,
                "months": months,
                "total": total,
            })
        rows.sort(key=lambda x: x["total"], reverse=True)

        wb = self._build_workbook(year, rows)

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        resp = HttpResponse(buf.getvalue(), content_type=XLSX_CONTENT_TYPE)
        resp["Content-Disposition"] = (
            f'attachment; filename="savdo_tushumlari_{year}.xlsx"'
        )
        return resp

    # ------------------------------------------------------------------
    def _build_workbook(self, year: int, rows: list[dict]) -> Workbook:
        thin = Side(style="thin", color="D9D9D9")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        header_fill = PatternFill("solid", fgColor="305496")
        header_font = Font(bold=True, color="FFFFFF")
        total_fill = PatternFill("solid", fgColor="DDEBF7")
        money_fmt = "#,##0"

        wb = Workbook()
        ws = wb.active
        ws.title = f"{year}"

        headers = ["№", "Tashkilot", "STIR", "Do'kon"] + MONTHS_UZ + ["Jami"]
        last_col = len(headers)

        # Sarlavha (merged)
        ws.merge_cells(
            start_row=1, start_column=1, end_row=1, end_column=last_col
        )
        title_cell = ws.cell(row=1, column=1)
        title_cell.value = (
            f"Savdo tushumlari (faktura + OKKM) — {year}-yil, "
            f"tashkilotlar bo'yicha oylik (so'm)"
        )
        title_cell.font = Font(bold=True, size=13)
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 24

        # Ustun sarlavhalari
        for col, text in enumerate(headers, start=1):
            c = ws.cell(row=2, column=col, value=text)
            c.fill = header_fill
            c.font = header_font
            c.alignment = Alignment(
                horizontal="center", vertical="center", wrap_text=True
            )
            c.border = border
        ws.row_dimensions[2].height = 30

        col_totals = [Decimal(0)] * 12
        grand_total = Decimal(0)

        row_idx = 3
        for i, r in enumerate(rows, start=1):
            ws.cell(row=row_idx, column=1, value=i).border = border
            ws.cell(row=row_idx, column=2, value=r["name"]).border = border
            ws.cell(row=row_idx, column=3, value=r["stir"]).border = border
            ws.cell(row=row_idx, column=4, value=r["shop"]).border = border
            for m in range(12):
                val = r["months"][m]
                c = ws.cell(row=row_idx, column=5 + m, value=float(val))
                c.number_format = money_fmt
                c.border = border
                col_totals[m] += val
            tc = ws.cell(
                row=row_idx, column=5 + 12, value=float(r["total"])
            )
            tc.number_format = money_fmt
            tc.font = Font(bold=True)
            tc.border = border
            grand_total += r["total"]
            row_idx += 1

        # Jami qatori
        ws.cell(row=row_idx, column=1, value="").border = border
        jami = ws.cell(row=row_idx, column=2, value="JAMI")
        jami.font = Font(bold=True)
        jami.fill = total_fill
        jami.border = border
        ws.cell(row=row_idx, column=3, value="").fill = total_fill
        ws.cell(row=row_idx, column=4, value="").fill = total_fill
        for m in range(12):
            c = ws.cell(row=row_idx, column=5 + m, value=float(col_totals[m]))
            c.number_format = money_fmt
            c.font = Font(bold=True)
            c.fill = total_fill
            c.border = border
        gc = ws.cell(row=row_idx, column=5 + 12, value=float(grand_total))
        gc.number_format = money_fmt
        gc.font = Font(bold=True)
        gc.fill = total_fill
        gc.border = border

        # Ustun kengliklari
        ws.column_dimensions["A"].width = 5
        ws.column_dimensions["B"].width = 34
        ws.column_dimensions["C"].width = 14
        ws.column_dimensions["D"].width = 22
        for m in range(12):
            ws.column_dimensions[get_column_letter(5 + m)].width = 13
        ws.column_dimensions[get_column_letter(5 + 12)].width = 16

        # Sarlavhalarni va birinchi ustunlarni muzlatish
        ws.freeze_panes = "E3"

        return wb
