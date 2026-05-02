import flet as ft
import re
from api import get_metar, get_taf, get_metar_raw, get_taf_raw, is_api_key_configured


# ---------- Безопасное получение вложенных полей ----------
def safe(data, *keys, default="?"):
    for k in keys:
        if isinstance(data, dict) and k in data:
            data = data[k]
        else:
            return default
    return data


# ---------- Компас-иконка ----------
def wind_compass_icon(deg):
    try:
        deg = int(deg)
    except:
        return "🧭"

    if 337 <= deg or deg < 23:
        return "🧭↑"
    if 23 <= deg < 68:
        return "🧭↗"
    if 68 <= deg < 113:
        return "🧭→"
    if 113 <= deg < 158:
        return "🧭↘"
    if 158 <= deg < 203:
        return "🧭↓"
    if 203 <= deg < 248:
        return "🧭↙"
    if 248 <= deg < 293:
        return "🧭←"
    if 293 <= deg < 337:
        return "🧭↖"

    return "🧭"


# ---------- Оптимальная полоса ----------
def analyze_runway_wind(wind_dir, runways):
    try:
        wind_dir = int(wind_dir)
    except:
        return None, None, None

    if not runways:
        return None, None, None

    best_runway = None
    best_delta = 999

    for rw in runways:
        try:
            hdg = int(rw[1:3]) * 10
        except:
            continue

        delta = abs(wind_dir - hdg)
        delta = min(delta, 360 - delta)

        if delta < best_delta:
            best_delta = delta
            best_runway = rw

    if best_runway is None:
        return None, None, None

    if best_delta < 30:
        icon = "🛫⬆️"
        text = "встречный"
    elif best_delta > 150:
        icon = "🛫⬇️"
        text = "попутный"
    elif 30 <= best_delta < 60:
        icon = "🛫↗"
        text = "боковой-встречный"
    elif 120 <= best_delta <= 150:
        icon = "🛫↘"
        text = "боковой-попутный"
    else:
        icon = "🛫➡️"
        text = "боковой"

    return best_runway, icon, text


# ---------- Давление ----------
def extract_pressure(raw):
    if not isinstance(raw, str):
        return "нет данных"

    m_q = re.search(r"\bQ(\d{4})\b", raw)
    if m_q:
        return f"Q{m_q.group(1)}"

    m_a = re.search(r"\bA(\d{4})\b", raw)
    if m_a:
        return f"A{m_a.group(1)}"

    return "нет данных"


class WeatherCard(ft.Container):
    """Блок METAR/TAF — берёт ICAO из FlightCard (DEP, ARR, ALTN)."""

    def __init__(self, flight_card, _theme=None):
        super().__init__()
        self.flight = flight_card
        self._theme = _theme

        # ---------- Вывод ----------
        self.dep_output = ft.Text("", selectable=True, size=14)
        self.arr_output = ft.Text("", selectable=True, size=14)
        self.altn_output = ft.Text("", selectable=True, size=14)

        # ---------- Контейнеры ----------
        self.dep_container = ft.Container(content=self.dep_output, opacity=0.0, scale=0.97, animate_opacity=300, animate_scale=300)
        self.arr_container = ft.Container(content=self.arr_output, opacity=0.0, scale=0.97, animate_opacity=300, animate_scale=300)
        self.altn_container = ft.Container(content=self.altn_output, opacity=0.0, scale=0.97, animate_opacity=300, animate_scale=300)

        # ---------- Кнопки ----------
        self.dep_metar_btn = None
        self.dep_taf_btn = None
        self.arr_metar_btn = None
        self.arr_taf_btn = None
        self.altn_metar_btn = None
        self.altn_taf_btn = None

        # Применить тему и собрать макет
        self._build_ui()

    def _build_ui(self):
        t = self._theme

        # ---------- Стили кнопок ----------
        def styled_button(text, handler, color):
            return ft.ElevatedButton(
                text,
                on_click=handler,
                bgcolor=color,
                color="white",
                height=32,
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=12),
                    shape=ft.RoundedRectangleBorder(radius=6)
                )
            )

        # ---------- Панели ----------
        dep_panel = ft.Column([
            ft.Text("✈️ DEPARTURE", size=16, weight="bold", color=t.weather_text),
            ft.Row([
                styled_button("🌤 METAR", self._load_dep_metar, "#16A34A"),
                styled_button("📄 TAF", self._load_dep_taf, "#2563EB"),
            ], spacing=8),
            self.dep_container,
        ], spacing=10, expand=True)

        arr_panel = ft.Column([
            ft.Text("🛬 ARRIVAL", size=16, weight="bold", color=t.weather_text),
            ft.Row([
                styled_button("🌤 METAR", self._load_arr_metar, "#16A34A"),
                styled_button("📄 TAF", self._load_arr_taf, "#2563EB"),
            ], spacing=8),
            self.arr_container,
        ], spacing=10, expand=True)

        altn_panel = ft.Column([
            ft.Text("🔄 ALTERNATE", size=16, weight="bold", color=t.weather_text),
            ft.Row([
                styled_button("🌤 METAR", self._load_altn_metar, "#16A34A"),
                styled_button("📄 TAF", self._load_altn_taf, "#2563EB"),
            ], spacing=8),
            self.altn_container,
        ], spacing=10, expand=True)

        # ---------- Контейнер секции ----------
        self.padding = 20
        self.bgcolor = t.weather_card_bg
        self.border_radius = 15
        self.border = ft.border.all(1, t.weather_border)

        # Применить цвет текста к выводу
        self.dep_output.color = t.weather_text
        self.arr_output.color = t.weather_text
        self.altn_output.color = t.weather_text

        # Сбросить панели к стилю по умолчанию
        panel_style = dict(
            padding=15,
            bgcolor=t.weather_panel_bg,
            border_radius=12,
            border=ft.border.all(2, t.weather_border),
        )
        for c in [self.dep_container, self.arr_container, self.altn_container]:
            c.padding = panel_style["padding"]
            c.bgcolor = panel_style["bgcolor"]
            c.border_radius = panel_style["border_radius"]
            c.border = panel_style["border"]

        self.content = ft.Column([
            ft.Text("WEATHER BRIEFING / ПОГОДА", size=15, weight="bold", color=t.title),
            ft.Container(height=8),
            ft.Row([dep_panel, arr_panel, altn_panel], spacing=20, alignment="start"),
        ], spacing=10)

    def apply_theme(self, theme):
        self._theme = theme
        self._build_ui()
        try:
            self.update()
        except Exception:
            pass

    # ---------- Вспомогательные ----------
    def _show_panel(self, c):
        c.opacity = 1
        c.scale = 1

    def _hide_panel(self, c):
        c.opacity = 0
        c.scale = 0.97

    def _get_icao(self, field_name):
        field = getattr(self.flight, field_name, None)
        if field:
            return (field.value or "").strip().upper()
        return ""

    def _update_page(self):
        try:
            if self.page:
                self.page.update()
        except Exception:
            pass

    def _show_no_api_key(self, output, container):
        """Показывает сообщение об отсутствии API-ключа."""
        t = self._theme
        self._hide_panel(container)
        output.value = "⚠️ API-ключ CheckWX не задан.\nУстановите переменную окружения CHECKWX_API_KEY."
        output.color = "orange"
        container.border = ft.border.all(2, "orange")
        container.bgcolor = "#3b2f0f"
        self._show_panel(container)
        self._update_page()

    # ---------- Форматирование METAR ----------
    def _format_metar(self, data, raw_text):
        t = self._theme

        if not isinstance(data, dict):
            return (
                f"Нет данных\nRAW: {raw_text}",
                t.weather_text,
                ft.border.all(2, t.weather_border),
                t.weather_panel_bg
            )

        fc = data.get("flight_category", "N/A")

        text_color = {
            "VFR": "lightgreen",
            "MVFR": "lightblue",
            "IFR": "pink",
            "LIFR": "violet",
        }.get(fc, t.weather_text)

        panel_bg = {
            "VFR": "#022c22",
            "MVFR": "#0f172a",
            "IFR": "#3b0f0f",
            "LIFR": "#3b0f3b",
        }.get(fc, t.weather_panel_bg)

        border_color = {
            "VFR": "#00FF00",
            "MVFR": "#00A2FF",
            "IFR": "#FF3B3B",
            "LIFR": "#C000FF",
        }.get(fc, t.weather_border)

        temp = safe(data, "temperature", "celsius")
        dew = safe(data, "dewpoint", "celsius")

        wind_dir = safe(data, "wind", "degrees")
        wind_speed = safe(data, "wind", "speed", "mps")
        compass = wind_compass_icon(wind_dir)

        vis = safe(data, "visibility", "meters")

        clouds = data.get("clouds", [])
        cloud_text = ", ".join([f"{c.get('code')} {c.get('feet')}ft" for c in clouds]) if clouds else "Clear"

        runways = []
        if isinstance(raw_text, str):
            matches = re.findall(r"R(\d{2}[LRC]?)(?=/| |$)", raw_text)
            for m in matches:
                rw = "R" + m
                if rw not in runways:
                    runways.append(rw)

        runways_text = ", ".join(runways) if runways else "нет"

        best_rw, wind_icon, wind_type = analyze_runway_wind(wind_dir, runways)

        if best_rw is None:
            wind_analysis = "Тип ветра: нет данных"
        else:
            wind_analysis = f"✈️ Тип: {wind_icon} {wind_type}\nОптимальная полоса: {best_rw}"

        pressure = extract_pressure(raw_text)

        text = (
            f"✈️ {data.get('icao', '?')}  |  Категория: {fc}\n"
            f"⏱ Давление: {pressure}\n"
            f"🌡 {temp}°C  💧 {dew}°C\n"
            f"🌬 {compass} {wind_dir}° {wind_speed} м/с\n"
            f"{wind_analysis}\n"
            f"🛬 Полоса: {runways_text}\n"
            f"👁 Видимость: {vis}\n"
            f"☁ {cloud_text}\n"
            f"RAW: {raw_text}"
        )

        return text, text_color, ft.border.all(2, border_color), panel_bg

    # ---------- Форматирование TAF ----------
    def _format_taf(self, data, raw_text):
        t = self._theme
        if not isinstance(data, dict):
            return f"Нет данных\nRAW: {raw_text}"

        period = data.get("period", {})

        return (
            f"🛫 {data.get('icao', '?')}\n"
            f"⏱ {period.get('from', '?')} → {period.get('to', '?')}\n"
            f"RAW: {raw_text}"
        )

    # ---------- Обработчики DEP ----------
    def _load_dep_metar(self, e):
        icao = self._get_icao("dep_input")
        if not icao:
            return
        if not is_api_key_configured():
            self._show_no_api_key(self.dep_output, self.dep_container)
            return
        data = get_metar(icao)
        raw = get_metar_raw(icao)
        self._hide_panel(self.dep_container)
        text, color, border, bg = self._format_metar(data, raw)
        self.dep_output.value = text
        self.dep_output.color = color
        self.dep_container.border = border
        self.dep_container.bgcolor = bg
        self._show_panel(self.dep_container)
        self._update_page()

    def _load_dep_taf(self, e):
        t = self._theme
        icao = self._get_icao("dep_input")
        if not icao:
            return
        if not is_api_key_configured():
            self._show_no_api_key(self.dep_output, self.dep_container)
            return
        data = get_taf(icao)
        raw = get_taf_raw(icao)
        self._hide_panel(self.dep_container)
        self.dep_output.value = self._format_taf(data, raw)
        self.dep_output.color = t.weather_text
        self.dep_container.border = ft.border.all(2, t.weather_border)
        self.dep_container.bgcolor = t.weather_panel_bg
        self._show_panel(self.dep_container)
        self._update_page()

    # ---------- Обработчики ARR ----------
    def _load_arr_metar(self, e):
        icao = self._get_icao("arr_input")
        if not icao:
            return
        if not is_api_key_configured():
            self._show_no_api_key(self.arr_output, self.arr_container)
            return
        data = get_metar(icao)
        raw = get_metar_raw(icao)
        self._hide_panel(self.arr_container)
        text, color, border, bg = self._format_metar(data, raw)
        self.arr_output.value = text
        self.arr_output.color = color
        self.arr_container.border = border
        self.arr_container.bgcolor = bg
        self._show_panel(self.arr_container)
        self._update_page()

    def _load_arr_taf(self, e):
        t = self._theme
        icao = self._get_icao("arr_input")
        if not icao:
            return
        if not is_api_key_configured():
            self._show_no_api_key(self.arr_output, self.arr_container)
            return
        data = get_taf(icao)
        raw = get_taf_raw(icao)
        self._hide_panel(self.arr_container)
        self.arr_output.value = self._format_taf(data, raw)
        self.arr_output.color = t.weather_text
        self.arr_container.border = ft.border.all(2, t.weather_border)
        self.arr_container.bgcolor = t.weather_panel_bg
        self._show_panel(self.arr_container)
        self._update_page()

    # ---------- Обработчики ALTN ----------
    def _load_altn_metar(self, e):
        icao = self._get_icao("altn_input")
        if not icao:
            return
        if not is_api_key_configured():
            self._show_no_api_key(self.altn_output, self.altn_container)
            return
        data = get_metar(icao)
        raw = get_metar_raw(icao)
        self._hide_panel(self.altn_container)
        text, color, border, bg = self._format_metar(data, raw)
        self.altn_output.value = text
        self.altn_output.color = color
        self.altn_container.border = border
        self.altn_container.bgcolor = bg
        self._show_panel(self.altn_container)
        self._update_page()

    def _load_altn_taf(self, e):
        t = self._theme
        icao = self._get_icao("altn_input")
        if not icao:
            return
        if not is_api_key_configured():
            self._show_no_api_key(self.altn_output, self.altn_container)
            return
        data = get_taf(icao)
        raw = get_taf_raw(icao)
        self._hide_panel(self.altn_container)
        self.altn_output.value = self._format_taf(data, raw)
        self.altn_output.color = t.weather_text
        self.altn_container.border = ft.border.all(2, t.weather_border)
        self.altn_container.bgcolor = t.weather_panel_bg
        self._show_panel(self.altn_container)
        self._update_page()
