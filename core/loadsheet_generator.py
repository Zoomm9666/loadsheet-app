# core/loadsheet_generator.py
"""Генерация PDF-документа Loadsheet (2 листа)."""

import os
from datetime import datetime
from fpdf import FPDF


# Кросс-платформенный поиск шрифтов
def _find_font(names):
    """Ищет шрифт по списку имён в разных ОС."""
    search_paths = [
        # Windows
        os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
        # Linux — Debian/Ubuntu
        "/usr/share/fonts/truetype/noto",
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/truetype/liberation",
        "/usr/share/fonts/truetype/freefont",
        # macOS
        "/System/Library/Fonts",
        "/Library/Fonts",
        # Проектные шрифты (для Docker)
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts"),
    ]
    for path in search_paths:
        for name in names:
            full = os.path.join(path, name)
            if os.path.exists(full):
                return full
    return None

FONT_ARIAL = _find_font(["arial.ttf", "NotoSans-Regular.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "FreeSans.ttf"])
FONT_ARIAL_BD = _find_font(["arialbd.ttf", "NotoSans-Bold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "FreeSansBold.ttf"])
FONT_ARIAL_I = _find_font(["ariali.ttf", "NotoSans-Italic.ttf", "DejaVuSans-Oblique.ttf", "LiberationSans-Italic.ttf", "FreeSansOblique.ttf"])
FONT_ARIAL_BI = _find_font(["arialbi.ttf", "NotoSans-BoldItalic.ttf", "DejaVuSans-BoldOblique.ttf", "LiberationSans-BoldItalic.ttf", "FreeSansBoldOblique.ttf"])
FONT_COURIER = _find_font(["consola.ttf", "NotoSansMono-Regular.ttf", "DejaVuSansMono.ttf", "LiberationMono-Regular.ttf"])


class LoadsheetPDF(FPDF):
    """Кастомный PDF с колонтитулами и рамкой."""

    def header(self):
        self.set_font("Arial", "B", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "LOADSHEET - CONFIDENTIAL", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(180, 180, 180)
        self.line(10, 12, 200, 12)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def _fmt(val, unit="KG"):
    """Форматирование числа с пробелом-разделителем."""
    return f"{val:,.0f} {unit}".replace(",", " ")


def _fmt_short(val):
    return f"{val:,.0f}".replace(",", " ")


def generate_loadsheet(data: dict, output_path: str = None) -> str:
    """
    Генерирует PDF Loadsheet из данных приложения (2 страницы).

    Args:
        data: словарь со всеми данными (flight, payload, fuel, weights)
        output_path: путь для сохранения PDF (если None - во временную папку)

    Returns:
        Путь к сгенерированному PDF-файлу
    """
    pdf = LoadsheetPDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Подключаем Unicode-шрифт Arial
    if os.path.exists(FONT_ARIAL):
        pdf.add_font("Arial", "", FONT_ARIAL, uni=True)
        if os.path.exists(FONT_ARIAL_BD):
            pdf.add_font("Arial", "B", FONT_ARIAL_BD, uni=True)
        if os.path.exists(FONT_ARIAL_I):
            pdf.add_font("Arial", "I", FONT_ARIAL_I, uni=True)
        if os.path.exists(FONT_ARIAL_BI):
            pdf.add_font("Arial", "BI", FONT_ARIAL_BI, uni=True)
    if os.path.exists(FONT_COURIER):
        pdf.add_font("Consolas", "", FONT_COURIER, uni=True)

    # Извлекаем данные
    flight = data.get("flight", {})
    payload = data.get("payload", {})
    fuel = data.get("fuel", {})
    weights = data.get("weights", {})
    ac = data.get("aircraft", {})

    now = datetime.now()
    date_str = now.strftime("%d %b %Y")
    time_str = now.strftime("%H:%M UTC")

    # ═══════════════════════════════════════════════════════════
    # ЛИСТ 1: СВОДКА ПОЛЁТА + ТОПЛИВО
    # ═══════════════════════════════════════════════════════════
    pdf.add_page()

    # Заголовок
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(30, 78, 140)
    pdf.cell(0, 10, "LOADSHEET", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Generated: {date_str} {time_str}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Рамка документа
    pdf.set_draw_color(30, 78, 140)
    pdf.set_line_width(0.5)
    pdf.rect(10, 10, 190, 277)

    # ── Левая колонка: Маршрут + Экипаж + Пассажиры ──
    col_w = 92  # ширина каждой колонки

    # Сохраняем X для левой колонки
    left_x = 12
    right_x = 108

    # === ЛЕВАЯ КОЛОНКА ===
    pdf.set_x(left_x)
    _section_header_small(pdf, "1. FLIGHT / ПОЛЁТ", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "DATE", date_str, col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "AIRCRAFT", ac.get("name", "---"), col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "ROUTE",
                    f"{flight.get('dep', '---')}-{flight.get('arr', '---')}/{flight.get('altn', '---')}", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "DIST", flight.get("distance", "---"), col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "ALTN", flight.get("altn_distance", "---"), col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "TIME", flight.get("time", "---"), col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "FL", flight.get("fl", "---"), col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "CI", str(flight.get("ci", "---")), col_w)
    pdf.ln(3)

    pdf.set_x(left_x)
    _section_header_small(pdf, "2. CREW / ЭКИПАЖ", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "CAPTAIN", f"{payload.get('captain', 0)} x 85", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "F/O", f"{payload.get('fo', 0)} x 85", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "CABIN", f"{payload.get('fa', 0)} x 75", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "CREW BAGS", f"{payload.get('crew_bag', 0)} x 10", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "CREW WT", _fmt(payload.get("crew_weight", 0)), col_w)
    pdf.ln(3)

    pdf.set_x(left_x)
    _section_header_small(pdf, "3. PAX / ПАССАЖИРЫ", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "ADULT", f"{payload.get('adult', 0)} x 85", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "CHILD", f"{payload.get('child', 0)} x 40", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "INF", f"{payload.get('inf', 0)} x 15", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "HAND LUGG", _fmt(payload.get("hand_luggage_weight", 0)), col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "TOTAL PAX", str(payload.get("total_pax", 0)), col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "PAX WEIGHT", _fmt(payload.get("pax_weight", 0)), col_w)
    pdf.ln(3)

    pdf.set_x(left_x)
    _section_header_small(pdf, "4. CARGO / ГРУЗ", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "BAGGAGE", f"{payload.get('bag_count', 0)} x {payload.get('bag_weight', 20)}", col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "CARGO", _fmt(payload.get("cargo", 0)), col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "MAIL", _fmt(payload.get("mail", 0)), col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "CATERING", _fmt(payload.get("catering_weight", 0)), col_w)
    pdf.set_x(left_x)
    _info_row_small(pdf, "WATER", _fmt(payload.get("water", 0)), col_w)

    # === ПРАВАЯ КОЛОНКА: ТОПЛИВО ===
    # Вертикальный разделитель
    y_start = pdf.get_y() - 120  # примерно
    pdf.set_draw_color(200, 200, 200)
    pdf.line(105, 30, 105, 280)

    # Возвращаемся наверх для правой колонки
    y_top = 30
    pdf.set_y(y_top)
    pdf.set_x(right_x)
    _section_header_small(pdf, "5. FUEL / ТОПЛИВО", col_w)

    # Таблица топлива
    pdf.set_x(right_x)
    pdf.set_font("Arial", "B", 8)
    pdf.set_fill_color(30, 78, 140)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(50, 6, "COMPONENT", border=1, fill=True)
    pdf.cell(22, 6, "KG", border=1, fill=True, align="R")
    pdf.cell(20, 6, "TIME", border=1, fill=True, align="R",
             new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 8)

    fuel_rows = [
        ("TRIP", fuel.get("trip_fuel", 0), f"{fuel.get('trip_time', 0)}m"),
        ("CONTINGENCY", fuel.get("contingency", 0), ""),
        ("FINAL RESERVE", fuel.get("reserve_fuel", 0), f"{fuel.get('final_time', 30)}m"),
        ("ALTN FUEL", fuel.get("alt_fuel", 0), f"{fuel.get('alt_time', 0)}m"),
        ("TAXI", fuel.get("taxi_fuel", 0), ""),
        ("APU", fuel.get("apu_fuel", 0), ""),
        ("HOLD", fuel.get("hold_fuel", 0), f"{fuel.get('hold_time', 30)}m"),
        ("ANTI-ICE", fuel.get("ice_penalty", 0), ""),
        ("EXTRA", fuel.get("extra_fuel", 0), ""),
    ]

    for i, (label, kg, time_val) in enumerate(fuel_rows):
        pdf.set_x(right_x)
        if i % 2 == 0:
            pdf.set_fill_color(245, 247, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.cell(50, 5, f" {label}", border=1, fill=True)
        pdf.cell(22, 5, _fmt_short(kg), border=1, fill=True, align="R")
        pdf.cell(20, 5, time_val, border=1, fill=True, align="R",
                 new_x="LMARGIN", new_y="NEXT")

    # Block Fuel
    pdf.set_x(right_x)
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(255, 248, 220)
    pdf.set_draw_color(217, 119, 6)
    pdf.cell(50, 7, "BLOCK FUEL", border=1, fill=True)
    pdf.cell(42, 7, _fmt(fuel.get("block_fuel", 0)), border=1, fill=True, align="R",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Fuel notes
    pdf.set_x(right_x)
    pdf.set_font("Arial", "", 7)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(col_w, 4, f"Burn: {ac.get('fuel_burn', 0)} kg/h | GS: {flight.get('gs', 0)} kts | Anti-ice: {'ON' if fuel.get('ice_on') else 'OFF'}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # === ПРАВАЯ КОЛОНКА: ВЕС ===
    pdf.set_x(right_x)
    _section_header_small(pdf, "6. WEIGHT / ВЕС", col_w)

    # Таблица весов
    pdf.set_x(right_x)
    pdf.set_font("Arial", "B", 8)
    pdf.set_fill_color(30, 78, 140)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(35, 6, "ITEM", border=1, fill=True)
    pdf.cell(22, 6, "KG", border=1, fill=True, align="R")
    pdf.cell(20, 6, "MAX", border=1, fill=True, align="R")
    pdf.cell(15, 6, "STATUS", border=1, fill=True, align="C",
             new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 8)

    weight_rows = [
        ("OEW", weights.get("oew", 0), None, "FIXED"),
        ("PAYLOAD", weights.get("payload", 0), None, "---"),
        ("ZFW", weights.get("zfw", 0), weights.get("mzfw", 0), ""),
        ("TOW", weights.get("tow", 0), weights.get("mtow", 0), ""),
        ("LW", weights.get("lw", 0), weights.get("mldw", 0), ""),
    ]

    for i, (label, val, max_val, status) in enumerate(weight_rows):
        pdf.set_x(right_x)
        if i % 2 == 0:
            pdf.set_fill_color(245, 247, 250)
        else:
            pdf.set_fill_color(255, 255, 255)

        if max_val is not None:
            exceeded = val > max_val
            status = "EXC!" if exceeded else "OK"
        elif status == "FIXED":
            status = "FIX"
        else:
            status = "---"

        pdf.cell(35, 5, f" {label}", border=1, fill=True)
        pdf.cell(22, 5, _fmt_short(val), border=1, fill=True, align="R")
        pdf.cell(20, 5, _fmt_short(max_val) if max_val is not None else "---", border=1, fill=True, align="R")

        if status == "EXC!":
            pdf.set_text_color(200, 0, 0)
            pdf.set_font("Arial", "B", 8)
        elif status == "OK":
            pdf.set_text_color(0, 130, 0)
            pdf.set_font("Arial", "B", 8)
        else:
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "", 8)

        pdf.cell(15, 5, status, border=1, fill=True, align="C",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 8)

    pdf.ln(4)

    # Формула веса
    pdf.set_x(right_x)
    pdf.set_font("Consolas", "", 8)
    pdf.cell(col_w, 4,
             f"OEW {_fmt_short(weights.get('oew', 0))} + PAX {_fmt_short(weights.get('payload', 0))} = ZFW {_fmt_short(weights.get('zfw', 0))}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(right_x)
    pdf.cell(col_w, 4,
             f"ZFW {_fmt_short(weights.get('zfw', 0))} + Fuel {_fmt_short(fuel.get('block_fuel', 0))} = TOW {_fmt_short(weights.get('tow', 0))}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(right_x)
    pdf.cell(col_w, 4,
             f"TOW {_fmt_short(weights.get('tow', 0))} - Trip {_fmt_short(fuel.get('trip_fuel', 0))} = LW {_fmt_short(weights.get('lw', 0))}",
             new_x="LMARGIN", new_y="NEXT")

    # ═══════════════════════════════════════════════════════════
    # ЛИСТ 2: ИТОГОВАЯ ТАБЛИЦА + ПОДПИСИ
    # ═══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.set_draw_color(30, 78, 140)
    pdf.set_line_width(0.5)
    pdf.rect(10, 10, 190, 277)

    # Заголовок
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(30, 78, 140)
    pdf.cell(0, 10, "LOADSHEET SUMMARY / ИТОГОВАЯ ТАБЛИЦА", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Полная таблица: маршрут ──
    _section_header(pdf, "FLIGHT / ПОЛЁТ")
    _info_row(pdf, "DATE / ДАТА", date_str)
    _info_row(pdf, "AIRCRAFT / САМОЛЁТ", ac.get("name", "---"))
    _info_row(pdf, "ROUTE / МАРШРУТ",
              f"{flight.get('dep', '---')} -> {flight.get('arr', '---')} / {flight.get('altn', '---')}")
    _info_row(pdf, "DISTANCE / ДАЛЬНОСТЬ", flight.get("distance", "---"))
    _info_row(pdf, "EST TIME / ВРЕМЯ ПОЛЁТА", flight.get("time", "---"))
    _info_row(pdf, "CRUISE FL / ЭШЕЛОН", flight.get("fl", "---"))
    pdf.ln(3)

    # ── Полная таблица: загрузка ──
    _section_header(pdf, "PAYLOAD / ЗАГРУЗКА")
    _info_row(pdf, "PAX (ADULT/CHILD/INF)",
              f"{payload.get('adult', 0)}/{payload.get('child', 0)}/{payload.get('inf', 0)} = {payload.get('total_pax', 0)} total")
    _info_row(pdf, "PAX WEIGHT / ВЕС ПАСС.", _fmt(payload.get("pax_weight", 0)))
    _info_row(pdf, "BAGGAGE / БАГАЖ", _fmt(payload.get("bag_total", 0)))
    _info_row(pdf, "CARGO / ГРУЗ", _fmt(payload.get("cargo", 0)))
    _info_row(pdf, "MAIL / ПОЧТА", _fmt(payload.get("mail", 0)))
    _info_row(pdf, "CREW / ЭКИПАЖ", _fmt(payload.get("crew_weight", 0)))
    _info_row(pdf, "CATERING / ПИТАНИЕ", _fmt(payload.get("catering_weight", 0)))
    _info_row(pdf, "WATER / ВОДА", _fmt(payload.get("water", 0)))

    # Итого Payload
    pdf.set_font("Arial", "B", 11)
    pdf.set_fill_color(255, 248, 220)
    pdf.set_draw_color(217, 119, 6)
    pdf.cell(95, 8, "TOTAL PAYLOAD / КОММ. ЗАГРУЗКА", border=1, fill=True)
    pdf.cell(95, 8, _fmt(payload.get("total_kg", 0)), border=1, align="R", fill=True,
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Полная таблица: топливо ──
    _section_header(pdf, "FUEL / ТОПЛИВО")
    _info_row(pdf, "TRIP FUEL / ПОЛЁТНОЕ", _fmt(fuel.get("trip_fuel", 0)))
    _info_row(pdf, "CONTINGENCY 5% / КОНТИНГ.", _fmt(fuel.get("contingency", 0)))
    _info_row(pdf, "FINAL RESERVE / КОН. РЕЗЕРВ", _fmt(fuel.get("reserve_fuel", 0)))
    _info_row(pdf, "ALTN FUEL / ЗАПАСН.", _fmt(fuel.get("alt_fuel", 0)))
    _info_row(pdf, "TAXI / ТАКСИ", _fmt(fuel.get("taxi_fuel", 0)))
    _info_row(pdf, "APU / ВСУ", _fmt(fuel.get("apu_fuel", 0)))
    _info_row(pdf, "HOLD / УДЕРЖАНИЕ", _fmt(fuel.get("hold_fuel", 0)))
    _info_row(pdf, "ANTI-ICE / ШТРАФ ОБЛ.", _fmt(fuel.get("ice_penalty", 0)))
    _info_row(pdf, "EXTRA / ДОП.", _fmt(fuel.get("extra_fuel", 0)))

    # Block Fuel
    pdf.set_font("Arial", "B", 11)
    pdf.set_fill_color(255, 248, 220)
    pdf.set_draw_color(217, 119, 6)
    pdf.cell(95, 8, "BLOCK FUEL / ЗАПРАВКА", border=1, fill=True)
    pdf.cell(95, 8, _fmt(fuel.get("block_fuel", 0)), border=1, align="R", fill=True,
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Полная таблица: вес ──
    _section_header(pdf, "WEIGHT / ВЕС")
    _info_row(pdf, "OEW / СНАРЯЖЁННЫЙ", _fmt(weights.get("oew", 0)))
    _info_row(pdf, "PAYLOAD / ЗАГРУЗКА", _fmt(weights.get("payload", 0)))
    _info_row(pdf, "ZFW / БЕЗ ТОПЛИВА", f"{_fmt(weights.get('zfw', 0))}  (MAX {_fmt_short(weights.get('mzfw', 0))})")
    _info_row(pdf, "TOW / ВЗЛЁТНЫЙ", f"{_fmt(weights.get('tow', 0))}  (MAX {_fmt_short(weights.get('mtow', 0))})")
    _info_row(pdf, "LW / ПОСАДОЧНЫЙ", f"{_fmt(weights.get('lw', 0))}  (MAX {_fmt_short(weights.get('mldw', 0))})")
    pdf.ln(6)

    # ── Подписи ──
    _section_header(pdf, "SIGNATURES / ПОДПИСИ")
    pdf.ln(8)
    pdf.set_font("Arial", "", 10)
    pdf.cell(90, 6, "Captain / КВС: ________________________", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.cell(90, 6, "Dispatcher / Диспетчер: ________________________", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, f"Document generated automatically by Aviation Loadsheet Pro | {date_str} {time_str}",
             align="C", new_x="LMARGIN", new_y="NEXT")

    # Финальная рамка
    pdf.set_draw_color(30, 78, 140)
    pdf.set_line_width(0.5)
    pdf.rect(10, 10, 190, 277)

    # Сохранение
    if output_path is None:
        import tempfile
        output_path = os.path.join(tempfile.gettempdir(), f"loadsheet_{now.strftime('%Y%m%d_%H%M%S')}.pdf")

    pdf.output(output_path)
    return output_path


# ── Вспомогательные функции ──────────────────────────────────

def _section_header(pdf, text):
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(30, 78, 140)
    pdf.set_fill_color(230, 240, 255)
    pdf.cell(0, 7, f"  {text}", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)


def _section_header_small(pdf, text, width):
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(30, 78, 140)
    pdf.set_fill_color(230, 240, 255)
    pdf.cell(width, 6, f" {text}", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)


def _info_row(pdf, label, value):
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(80, 5, f"  {label}")
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, str(value), new_x="LMARGIN", new_y="NEXT")


def _info_row_small(pdf, label, value, width):
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(35, 5, f" {label}")
    pdf.set_font("Arial", "B", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(width - 35, 5, str(value), new_x="LMARGIN", new_y="NEXT")
