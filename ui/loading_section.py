import flet as ft


class LoadingCard(ft.Container):
    """Блок 2: PAYLOAD / ЗАГРУЗКА — детальная разбивка по категориям."""

    # ── Массы по умолчанию (кг) ──────────────────────────────────
    ADULT_KG = 85
    CHILD_KG = 40
    INF_KG = 15
    HAND_LUGGAGE_KG = 8
    CAPTAIN_KG = 85
    FO_KG = 85
    FA_KG = 75
    CREW_BAG_KG = 10
    CATERING_PER_PAX_KG = 10

    def __init__(self, on_change_callback, _theme=None):
        super().__init__()
        self.on_change_callback = on_change_callback
        self._theme = _theme

        # ═══ РЯД 1: ПАССАЖИРЫ ══════════════════════════════════
        self.adult_input = ft.TextField(label="ADULT (85 kg)", value="0", width=90, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)
        self.child_input = ft.TextField(label="CHILD (40 kg)", value="0", width=90, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)
        self.inf_input = ft.TextField(label="INF (15 kg)", value="0", width=90, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)
        self.hand_luggage_input = ft.TextField(label="HAND LUGG (8 kg)", value="0", width=90, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)

        # ═══ РЯД 2: БАГАЖ ══════════════════════════════════════
        self.bag_weight_dropdown = ft.Dropdown(
            label="BAG KG",
            width=100,
            options=[ft.dropdown.Option(str(w)) for w in [5, 10, 15, 20, 23]],
            value="20",
            content_padding=5,
        )
        self.bag_count_input = ft.TextField(label="BAG COUNT", value="0", width=100, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)
        self.bag_total_txt = ft.Text("0 KG")

        # ═══ РЯД 3: ЭКИПАЖ ═════════════════════════════════════
        self.captain_input = ft.TextField(label="CAPTAIN (85)", value="1", width=90, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)
        self.fo_input = ft.TextField(label="F/O (85)", value="1", width=90, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)
        self.fa_input = ft.TextField(label="CABIN CREW (75)", value="0", width=90, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)
        self.crew_bag_input = ft.TextField(label="CREW BAG (10)", value="0", width=90, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)

        # ═══ РЯД 4: ПРОЧЕЕ ═════════════════════════════════════
        self.catering_input = ft.TextField(label="CATERING/PAX", value="10", width=100, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)
        self.water_input = ft.TextField(label="WATER KG", value="100", width=100, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)
        self.cargo_input = ft.TextField(label="CARGO KG", value="0", width=100, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)
        self.mail_input = ft.TextField(label="MAIL KG", value="0", width=100, height=48, text_align="center", border_radius=8, content_padding=5, keyboard_type=ft.KeyboardType.NUMBER)

        # ═══ ИТОГО ═════════════════════════════════════════════
        self.pax_total_txt = ft.Text("0 PAX")
        self.payload_total_txt = ft.Text("0 KG")

        # ── Привязка событий ───────────────────────────────────
        for ctrl in [
            self.adult_input, self.child_input, self.inf_input,
            self.hand_luggage_input,
            self.bag_weight_dropdown, self.bag_count_input,
            self.captain_input, self.fo_input, self.fa_input, self.crew_bag_input,
            self.catering_input, self.water_input, self.cargo_input, self.mail_input,
        ]:
            ctrl.on_change = self._handle_change

        # Применить тему и собрать макет
        self._build_ui()

    def _build_ui(self):
        t = self._theme

        # ── Стили из темы ─────────────────────────────────────
        SECTION_TITLE = ft.TextStyle(size=12, weight="bold", color=t.section_title)
        INPUT_STYLE = ft.TextStyle(size=14, weight="bold", color=t.input_text)
        RESULT_STYLE = ft.TextStyle(size=14, weight="bold", color=t.value)

        # Применить стили к полям ввода
        for f in [self.adult_input, self.child_input, self.inf_input,
                  self.hand_luggage_input, self.bag_count_input,
                  self.captain_input, self.fo_input, self.fa_input, self.crew_bag_input,
                  self.catering_input, self.water_input, self.cargo_input, self.mail_input]:
            f.text_style = INPUT_STYLE

        self.bag_weight_dropdown.text_style = INPUT_STYLE
        self.bag_total_txt.style = RESULT_STYLE
        self.pax_total_txt.style = ft.TextStyle(size=13, weight="bold", color=t.section_title)
        self.payload_total_txt.style = ft.TextStyle(size=18, weight="bold", color=t.accent)

        # ── Сборка макета ──────────────────────────────────────
        self.padding = 20
        self.bgcolor = t.card_bg
        self.border_radius = 15
        self.border = ft.border.all(1, t.card_border)

        self.content = ft.Column([
            # Заголовок
            ft.Text("2. PAYLOAD / ЗАГРУЗКА", size=15, weight="bold", color=t.title),
            ft.Divider(height=1, color=t.divider),
            ft.Container(height=6),

            # Горизонтальная компоновка: ввод слева — итоги справа
            ft.Row([
                # ═══ ЛЕВАЯ ЧАСТЬ: ВВОД ═══
                ft.Column([
                    # ── Ряд 1: Пассажиры ──
                    ft.Text("PASSENGERS / ПАССАЖИРЫ", style=SECTION_TITLE),
                    ft.Container(height=3),
                    ft.Row([
                        self.adult_input,
                        self.child_input,
                        self.inf_input,
                        self.hand_luggage_input,
                    ], spacing=10, wrap=True),

                    ft.Container(height=8),

                    # ── Ряд 2: Багаж ──
                    ft.Text("BAGGAGE / БАГАЖ", style=SECTION_TITLE),
                    ft.Container(height=3),
                    ft.Row([
                        self.bag_weight_dropdown,
                        self.bag_count_input,
                        ft.Container(content=self.bag_total_txt, padding=ft.padding.only(top=12)),
                    ], spacing=10),

                    ft.Container(height=8),

                    # ── Ряд 3: Экипаж ──
                    ft.Text("CREW / ЭКИПАЖ", style=SECTION_TITLE),
                    ft.Container(height=3),
                    ft.Row([
                        self.captain_input,
                        self.fo_input,
                        self.fa_input,
                        self.crew_bag_input,
                    ], spacing=10, wrap=True),

                    ft.Container(height=8),

                    # ── Ряд 4: Прочее ──
                    ft.Text("OTHER / ПРОЧЕЕ", style=SECTION_TITLE),
                    ft.Container(height=3),
                    ft.Row([
                        self.catering_input,
                        self.water_input,
                        self.cargo_input,
                        self.mail_input,
                    ], spacing=10, wrap=True),
                ], spacing=4, expand=True),

                ft.VerticalDivider(width=15, color=t.divider),

                # ═══ ПРАВАЯ ЧАСТЬ: ИТОГИ ═══
                ft.Column([
                    ft.Text("PAYLOAD SUMMARY", size=13, weight="bold", color=t.accent),
                    ft.Container(height=10),

                    # TOTAL PAX — в рамке
                    ft.Container(
                        content=ft.Column([
                            ft.Text("TOTAL PAX", style=ft.TextStyle(size=10, weight="bold", color=t.label_en)),
                            self.pax_total_txt,
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                        bgcolor=t.card_bg,
                        border_radius=12,
                        padding=ft.padding.symmetric(vertical=14, horizontal=20),
                        border=ft.border.all(1, t.card_border),
                        width=170,
                    ),

                    ft.Container(height=12),

                    # TOTAL PAYLOAD — крупный итог в рамке
                    ft.Container(
                        content=ft.Column([
                            ft.Text("TOTAL PAYLOAD", style=ft.TextStyle(size=10, weight="bold", color=t.label_en)),
                            self.payload_total_txt,
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                        bgcolor=t.total_bg,
                        border_radius=12,
                        padding=ft.padding.symmetric(vertical=18, horizontal=20),
                        border=ft.border.all(2, t.total_border),
                        width=170,
                    ),
                ], spacing=4, width=200, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ], vertical_alignment=ft.CrossAxisAlignment.START),
        ], spacing=4)

    def apply_theme(self, theme):
        self._theme = theme
        self._build_ui()
        try:
            self.update()
        except Exception:
            pass

    # ── Методы ─────────────────────────────────────────────────

    def _handle_change(self, e):
        self._update_bag_total()
        if self.on_change_callback:
            self.on_change_callback()

    def _update_bag_total(self):
        try:
            bag_w = int(self.bag_weight_dropdown.value or 20)
            bag_n = int(self.bag_count_input.value or 0)
            total = bag_w * bag_n
            self.bag_total_txt.value = f"{total:,} KG".replace(",", " ")
        except ValueError:
            self.bag_total_txt.value = "0 KG"

    def _safe_int(self, field, default=0):
        try:
            return int(field.value or default)
        except ValueError:
            return default

    def _safe_float(self, field, default=0):
        try:
            return float(field.value or default)
        except ValueError:
            return default

    def get_payload_data(self):
        """Возвращает детальную разбивку payload."""
        adult = self._safe_int(self.adult_input)
        child = self._safe_int(self.child_input)
        inf = self._safe_int(self.inf_input)
        hand_lug = self._safe_int(self.hand_luggage_input)

        bag_w = int(self.bag_weight_dropdown.value or 20)
        bag_n = self._safe_int(self.bag_count_input)
        bag_total = bag_w * bag_n

        captain = self._safe_int(self.captain_input)
        fo = self._safe_int(self.fo_input)
        fa = self._safe_int(self.fa_input)
        crew_bag = self._safe_int(self.crew_bag_input)

        catering_per_pax = self._safe_float(self.catering_input, 10)
        water = self._safe_float(self.water_input, 100)
        cargo = self._safe_float(self.cargo_input)
        mail = self._safe_float(self.mail_input)

        total_pax = adult + child + inf

        pax_weight = (adult * self.ADULT_KG
                      + child * self.CHILD_KG
                      + inf * self.INF_KG)

        hand_luggage_weight = hand_lug * self.HAND_LUGGAGE_KG

        crew_weight = (captain * self.CAPTAIN_KG
                       + fo * self.FO_KG
                       + fa * self.FA_KG
                       + crew_bag * self.CREW_BAG_KG)

        catering_weight = total_pax * catering_per_pax

        total_kg = (pax_weight + hand_luggage_weight + bag_total
                    + crew_weight + catering_weight + water + cargo + mail)

        self.pax_total_txt.value = f"{total_pax} PAX"
        self.payload_total_txt.value = f"{total_kg:,.0f} KG".replace(",", " ")
        self._update_bag_total()

        return {
            "adult": adult,
            "child": child,
            "inf": inf,
            "total_pax": total_pax,
            "pax_weight": pax_weight,
            "hand_luggage_weight": hand_luggage_weight,
            "bag_total": bag_total,
            "crew_weight": crew_weight,
            "catering_weight": catering_weight,
            "water": water,
            "cargo": cargo,
            "mail": mail,
            "total_kg": total_kg,
        }
