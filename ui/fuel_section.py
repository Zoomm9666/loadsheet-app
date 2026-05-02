import flet as ft


class FuelCard(ft.Container):
    """Блок 3: Расчёт заправки топливом. Три подраздела горизонтально."""

    def __init__(self, on_change_callback=None, _theme=None):
        super().__init__()
        self.on_change_callback = on_change_callback
        self._theme = _theme

        # ── Поля ввода (ПОДРАЗДЕЛ 1: ВВОД) ─────────────────────
        self.taxi_input = ft.TextField(
            label="TAXI FUEL KG", value="200",
            width=150, height=50, text_align="center",
            border_radius=8, content_padding=5,
        )
        self.apu_input = ft.TextField(
            label="APU FUEL KG", value="60",
            width=150, height=50, text_align="center",
            border_radius=8, content_padding=5,
        )
        self.extra_input = ft.TextField(
            label="EXTRA FUEL KG", value="800",
            width=150, height=50, text_align="center",
            border_radius=8, content_padding=5,
        )
        self.hold_input = ft.TextField(
            label="HOLD MIN", value="30",
            width=150, height=50, text_align="center",
            border_radius=8, content_padding=5,
        )
        self.ice_switch = ft.Switch(
            label="ANTI-ICE",
            value=False,
        )
        # Время полёта — отображается только для чтения (берётся из блока 1)
        self.flight_time_txt = ft.Text("0:00")

        # Привязка событий
        self.taxi_input.on_change = self._on_input_change
        self.apu_input.on_change = self._on_input_change
        self.extra_input.on_change = self._on_input_change
        self.hold_input.on_change = self._on_input_change
        self.ice_switch.on_change = self._on_input_change

        # ── Тексты результатов (ПОДРАЗДЕЛ 2: РАСХОД ТОПЛИВА) ───
        self.trip_fuel_txt = ft.Text("0 KG")
        self.trip_time_txt = ft.Text("0 min")
        self.contingency_txt = ft.Text("0 KG")
        self.reserve_txt = ft.Text("0 KG")
        self.reserve_time_txt = ft.Text("30 min")
        self.alt_fuel_txt = ft.Text("0 KG")
        self.alt_time_txt = ft.Text("0 min")
        self.taxi_txt = ft.Text("0 KG")
        self.apu_txt = ft.Text("0 KG")
        self.hold_fuel_txt = ft.Text("0 KG")
        self.hold_time_txt = ft.Text("30 min")
        self.ice_txt = ft.Text("0 KG")
        self.extra_txt = ft.Text("0 KG")

        # ── ПОДРАЗДЕЛ 3: BLOCK FUEL ─────────────────────────────
        self.block_fuel_txt = ft.Text("0 KG")
        self.tow_txt = ft.Text("0 KG")
        self.tow_limit_txt = ft.Text("")
        self.lw_txt = ft.Text("0 KG")
        self.lw_limit_txt = ft.Text("")

        # ── СТРОКА МАССЫ (горизонтальная) ────────────────────────
        self.oew_val_txt = ft.Text("0")
        self.oew_limit_txt = ft.Text("")

        self.payload_val_txt = ft.Text("0")
        self.payload_limit_txt = ft.Text("")

        self.zfw_val_txt = ft.Text("0")
        self.zfw_limit_txt = ft.Text("")

        self.tow_val_txt = ft.Text("0")
        self.tow_limit_txt2 = ft.Text("")

        self.lw_val_txt = ft.Text("0")
        self.lw_limit_txt2 = ft.Text("")

        # Контейнеры weight_box — храним ссылки для динамической смены фона
        self.oew_box = ft.Container()
        self.payload_box = ft.Container()
        self.zfw_box = ft.Container()
        self.tow_box = ft.Container()
        self.lw_box = ft.Container()

        # Применить тему и собрать макет
        self._build_ui()

    def _build_ui(self):
        t = self._theme

        # ── Стили из темы ─────────────────────────────────────
        LABEL_EN = ft.TextStyle(size=11, weight="bold", color=t.label_en)
        LABEL_RU = ft.TextStyle(size=9, color=t.label_ru)
        VALUE_STYLE = ft.TextStyle(size=14, weight="bold", color=t.value)
        TOTAL_STYLE = ft.TextStyle(size=22, weight="bold", color=t.accent)
        LIMIT_WARN = ft.TextStyle(size=12, weight="bold", color=t.limit_warn)
        INPUT_STYLE = ft.TextStyle(size=15, weight="bold", color=t.input_text)
        SECTION_TITLE = ft.TextStyle(size=12, weight="bold", color=t.section_title)

        WEIGHT_VAL = ft.TextStyle(size=15, weight="bold", color=t.green_text)
        WEIGHT_LIMIT = ft.TextStyle(size=10, color=t.limit_ok)
        WEIGHT_LABEL = ft.TextStyle(size=9, weight="bold", color=t.label_en)
        WEIGHT_LABEL_RU = ft.TextStyle(size=7, color=t.label_ru)

        def lang_label(en, ru):
            return ft.Column([
                ft.Text(en, style=LABEL_EN),
                ft.Text(ru, style=LABEL_RU),
            ], spacing=0, alignment=ft.MainAxisAlignment.CENTER)

        def result_row(label_en, label_ru, text_control):
            return ft.Row([
                ft.Container(
                    content=lang_label(label_en, label_ru),
                    width=155,
                ),
                text_control,
            ], alignment=ft.MainAxisAlignment.START)

        # Применить стили к полям ввода
        for f in [self.taxi_input, self.apu_input, self.extra_input, self.hold_input]:
            f.text_style = INPUT_STYLE

        # Применить стили к текстам результатов
        self.flight_time_txt.style = ft.TextStyle(size=16, weight="bold", color=t.value)
        for txt in [self.trip_fuel_txt, self.trip_time_txt, self.contingency_txt,
                     self.reserve_txt, self.reserve_time_txt, self.alt_fuel_txt,
                     self.alt_time_txt, self.taxi_txt, self.apu_txt,
                     self.hold_fuel_txt, self.hold_time_txt, self.ice_txt, self.extra_txt]:
            txt.style = VALUE_STYLE

        self.block_fuel_txt.style = TOTAL_STYLE
        self.tow_txt.style = VALUE_STYLE
        self.tow_limit_txt.style = LIMIT_WARN
        self.lw_txt.style = VALUE_STYLE
        self.lw_limit_txt.style = LIMIT_WARN

        # Весовые тексты
        self.oew_val_txt.style = WEIGHT_VAL
        self.oew_limit_txt.style = WEIGHT_LIMIT
        self.payload_val_txt.style = WEIGHT_VAL
        self.payload_limit_txt.style = WEIGHT_LIMIT
        self.zfw_val_txt.style = WEIGHT_VAL
        self.zfw_limit_txt.style = WEIGHT_LIMIT
        self.tow_val_txt.style = WEIGHT_VAL
        self.tow_limit_txt2.style = WEIGHT_LIMIT
        self.lw_val_txt.style = WEIGHT_VAL
        self.lw_limit_txt2.style = WEIGHT_LIMIT

        def weight_box(label_en, label_ru, val_txt, limit_txt, box_container):
            box_container.content = ft.Column([
                ft.Text(label_en, style=WEIGHT_LABEL, text_align="center"),
                ft.Text(label_ru, style=WEIGHT_LABEL_RU, text_align="center"),
                ft.Container(height=2),
                val_txt,
                limit_txt,
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            box_container.bgcolor = t.green_bg
            box_container.border_radius = 10
            box_container.padding = ft.padding.symmetric(vertical=8, horizontal=12)
            box_container.border = ft.border.all(1, t.green_border)
            box_container.width = 130
            return box_container

        # ── Сборка макета ─────────────────────────────────────
        self.padding = 25
        self.bgcolor = t.card_bg
        self.border_radius = 15
        self.border = ft.border.all(1, t.card_border)

        self.content = ft.Column([
            # Заголовок
            ft.Text("3. FUEL CALCULATION / РАСЧЁТ ЗАПРАВКИ", size=15, weight="bold", color=t.title),
            ft.Divider(height=1, color=t.divider),
            ft.Container(height=8),

            # Три подраздела горизонтально
            ft.Row([
                # ═══ ПОДРАЗДЕЛ 1: ВВОД ═══
                ft.Column([
                    ft.Text("INPUT / ВВОД", style=SECTION_TITLE),
                    ft.Container(height=5),
                    self.taxi_input,
                    ft.Container(height=5),
                    self.apu_input,
                    ft.Container(height=5),
                    # Время полёта (из блока 1, только чтение)
                    ft.Row([
                        lang_label("FLIGHT TIME", "ВРЕМЯ ПОЛЁТА"),
                        ft.Container(width=8),
                        self.flight_time_txt,
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Container(height=5),
                    self.extra_input,
                    ft.Container(height=5),
                    self.hold_input,
                    ft.Container(height=5),
                    self.ice_switch,
                ], spacing=3, width=180),

                ft.VerticalDivider(width=15, color=t.divider),

                # ═══ ПОДРАЗДЕЛ 2: РАСХОД ТОПЛИВА ═══
                ft.Column([
                    ft.Text("FUEL BREAKDOWN / РАСХОД ТОПЛИВА", style=SECTION_TITLE),
                    ft.Container(height=3),

                    result_row("TRIP FUEL", "ПОЛЁТНОЕ ТОПЛИВО", self.trip_fuel_txt),
                    result_row("TRIP TIME", "ВРЕМЯ ПОЛЁТА", self.trip_time_txt),
                    ft.Divider(height=1, color=t.divider),

                    result_row("CONTINGENCY 5%", "КОНТИНГЕНЦИЯ", self.contingency_txt),
                    result_row("FINAL RESERVE", "КОНЕЧНЫЙ РЕЗЕРВ", self.reserve_txt),
                    result_row("RESERVE TIME", "ВРЕМЯ РЕЗЕРВА", self.reserve_time_txt),
                    ft.Divider(height=1, color=t.divider),

                    result_row("ALTN FUEL", "ТОПЛИВО ЗАПАСН.", self.alt_fuel_txt),
                    result_row("ALTN TIME", "ВРЕМЯ ДО ЗАПАСН.", self.alt_time_txt),
                    ft.Divider(height=1, color=t.divider),

                    result_row("TAXI FUEL", "ТАКСИ", self.taxi_txt),
                    result_row("APU FUEL", "ВСУ", self.apu_txt),
                    result_row("HOLD FUEL", "УДЕРЖАНИЕ", self.hold_fuel_txt),
                    result_row("HOLD TIME", "ВРЕМЯ УДЕРЖ.", self.hold_time_txt),
                    result_row("ANTI-ICE PENALTY", "ШТРАФ ОБЛ.", self.ice_txt),
                    result_row("EXTRA FUEL", "ДОП. ТОПЛИВО", self.extra_txt),
                ], spacing=4, expand=True),

                ft.VerticalDivider(width=15, color=t.divider),

                # ═══ ПОДРАЗДЕЛ 3: BLOCK FUEL ═══
                ft.Column([
                    ft.Text("BLOCK FUEL", size=13, weight="bold", color=t.accent),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column([
                            self.block_fuel_txt,
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=t.total_bg,
                        border_radius=12,
                        padding=ft.padding.symmetric(vertical=18, horizontal=20),
                        border=ft.border.all(2, t.total_border),
                        width=190,
                    ),
                ], spacing=4, width=210, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ], vertical_alignment=ft.CrossAxisAlignment.START),

            # ═══ СТРОКА МАССЫ (горизонтальная) ═══
            ft.Container(height=12),
            ft.Divider(height=1, color=t.divider),
            ft.Container(height=4),
            ft.Text("WEIGHT SUMMARY / СВОДКА МАССЫ", size=12, weight="bold", color=t.title),
            ft.Container(height=6),
            ft.Row([
                weight_box("OEW", "СНАРЯЖЁННЫЙ", self.oew_val_txt, self.oew_limit_txt, self.oew_box),
                ft.Text("+", size=20, weight="bold", color=t.arrow),
                weight_box("PAYLOAD", "ЗАГРУЗКА", self.payload_val_txt, self.payload_limit_txt, self.payload_box),
                ft.Text("=", size=20, weight="bold", color=t.arrow),
                weight_box("ZFW", "БЕЗ ТОПЛИВА", self.zfw_val_txt, self.zfw_limit_txt, self.zfw_box),
                ft.Text("+", size=20, weight="bold", color=t.arrow),
                weight_box("TOW", "ВЗЛЁТНЫЙ", self.tow_val_txt, self.tow_limit_txt2, self.tow_box),
                ft.Text("→", size=20, weight="bold", color=t.arrow),
                weight_box("LW", "ПОСАДОЧНЫЙ", self.lw_val_txt, self.lw_limit_txt2, self.lw_box),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        ], spacing=8)

    def apply_theme(self, theme):
        self._theme = theme
        self._build_ui()
        try:
            self.update()
        except Exception:
            pass

    # ── Методы ─────────────────────────────────────────────────

    def _on_input_change(self, e):
        if self.on_change_callback:
            self.on_change_callback()

    def update_ui(self, fuel_data, tow, lw, mtow, mldw, flight_time_str="0:00",
                  oew=0, payload=0, zfw=0, mzfw=0):
        """Обновляет все результаты расчёта топлива."""
        t = self._theme

        def fmt(val, unit="KG"):
            return f"{val:,.0f} {unit}".replace(",", " ")

        def fmt_short(val):
            return f"{val:,.0f}".replace(",", " ")

        # Время полёта из первого блока
        self.flight_time_txt.value = flight_time_str

        # Топливные составляющие
        self.trip_fuel_txt.value = fmt(fuel_data["trip_fuel"])
        self.trip_time_txt.value = fmt(fuel_data["trip_time"], "min")
        self.contingency_txt.value = fmt(fuel_data["contingency"])
        self.reserve_txt.value = fmt(fuel_data["reserve_fuel"])
        self.reserve_time_txt.value = fmt(fuel_data["final_time"], "min")
        self.alt_fuel_txt.value = fmt(fuel_data["alt_fuel"])
        self.alt_time_txt.value = fmt(fuel_data["alt_time"], "min")
        self.taxi_txt.value = fmt(fuel_data["taxi_fuel"])
        self.apu_txt.value = fmt(fuel_data["apu_fuel"])
        self.hold_fuel_txt.value = fmt(fuel_data["hold_fuel"])
        self.hold_time_txt.value = fmt(fuel_data["hold_time"], "min")
        self.ice_txt.value = fmt(fuel_data["ice_penalty"])
        self.extra_txt.value = fmt(fuel_data["extra_fuel"])

        # Block Fuel
        self.block_fuel_txt.value = fmt(fuel_data["block_fuel"])

        # TOW с проверкой лимита (старый блок)
        self.tow_txt.value = fmt(tow)
        if tow > mtow:
            self.tow_txt.color = t.limit_warn
            self.tow_limit_txt.value = f"LIMIT {fmt(mtow)}"
            self.tow_limit_txt.color = t.limit_warn
        else:
            self.tow_txt.color = t.value
            self.tow_limit_txt.value = f"LIMIT {fmt(mtow)}"
            self.tow_limit_txt.color = t.limit_ok

        # LW с проверкой лимита (старый блок)
        self.lw_txt.value = fmt(lw)
        if lw > mldw:
            self.lw_txt.color = t.limit_warn
            self.lw_limit_txt.value = f"LIMIT {fmt(mldw)}"
            self.lw_limit_txt.color = t.limit_warn
        else:
            self.lw_txt.color = t.value
            self.lw_limit_txt.value = f"LIMIT {fmt(mldw)}"
            self.lw_limit_txt.color = t.limit_ok

        # ═══ СТРОКА МАССЫ ═══
        # OEW — фиксированный вес, всегда зелёный
        self.oew_val_txt.value = fmt_short(oew)
        self.oew_val_txt.color = t.green_text
        self.oew_limit_txt.value = ""
        self.oew_box.bgcolor = t.green_bg
        self.oew_box.border = ft.border.all(1, t.green_border)

        # Payload — без жёсткого лимита, всегда зелёный
        self.payload_val_txt.value = fmt_short(payload)
        self.payload_val_txt.color = t.green_text
        self.payload_limit_txt.value = ""
        self.payload_box.bgcolor = t.green_bg
        self.payload_box.border = ft.border.all(1, t.green_border)

        # ZFW с проверкой MZFW
        self.zfw_val_txt.value = fmt_short(zfw)
        self.zfw_limit_txt.value = f"MAX {fmt_short(mzfw)}"
        if zfw > mzfw:
            self.zfw_val_txt.color = t.red_text
            self.zfw_limit_txt.color = t.red_text
            self.zfw_box.bgcolor = t.red_bg
            self.zfw_box.border = ft.border.all(2, t.red_border)
        else:
            self.zfw_val_txt.color = t.green_text
            self.zfw_limit_txt.color = t.limit_ok
            self.zfw_box.bgcolor = t.green_bg
            self.zfw_box.border = ft.border.all(1, t.green_border)

        # TOW с проверкой MTOW
        self.tow_val_txt.value = fmt_short(tow)
        self.tow_limit_txt2.value = f"MAX {fmt_short(mtow)}"
        if tow > mtow:
            self.tow_val_txt.color = t.red_text
            self.tow_limit_txt2.color = t.red_text
            self.tow_box.bgcolor = t.red_bg
            self.tow_box.border = ft.border.all(2, t.red_border)
        else:
            self.tow_val_txt.color = t.green_text
            self.tow_limit_txt2.color = t.limit_ok
            self.tow_box.bgcolor = t.green_bg
            self.tow_box.border = ft.border.all(1, t.green_border)

        # LW с проверкой MLDW
        self.lw_val_txt.value = fmt_short(lw)
        self.lw_limit_txt2.value = f"MAX {fmt_short(mldw)}"
        if lw > mldw:
            self.lw_val_txt.color = t.red_text
            self.lw_limit_txt2.color = t.red_text
            self.lw_box.bgcolor = t.red_bg
            self.lw_box.border = ft.border.all(2, t.red_border)
        else:
            self.lw_val_txt.color = t.green_text
            self.lw_limit_txt2.color = t.limit_ok
            self.lw_box.bgcolor = t.green_bg
            self.lw_box.border = ft.border.all(1, t.green_border)

        self.update()
