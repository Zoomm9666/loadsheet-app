import flet as ft
from data.airport_manager import load_airports
from core.physics import get_distance, get_bearing

class FlightCard(ft.Container):
    def __init__(self, on_change_callback, _theme=None):
        super().__init__()
        self.on_change_callback = on_change_callback
        self._theme = _theme
        self.airports_data = load_airports()

        # База данных самолетов
        self.aircraft_presets = {
            "A319":     {"burn": 2300, "ECON": "15", "STD": "35", "FAST": "70", "TAS": 450},
            "A320CFM":  {"burn": 2400, "ECON": "15", "STD": "35", "FAST": "70", "TAS": 450},
            "A320IAE":  {"burn": 2450, "ECON": "15", "STD": "35", "FAST": "70", "TAS": 450},
            "A320NEO":  {"burn": 2200, "ECON": "15", "STD": "35", "FAST": "70", "TAS": 450},
            "A321":     {"burn": 2600, "ECON": "15", "STD": "35", "FAST": "70", "TAS": 450},
            "B737-700": {"burn": 2400, "ECON": "10", "STD": "30", "FAST": "65", "TAS": 445},
            "B737-800": {"burn": 2600, "ECON": "10", "STD": "30", "FAST": "65", "TAS": 445},
            "B737-900": {"burn": 2700, "ECON": "10", "STD": "30", "FAST": "65", "TAS": 445},
        }

        # Поля ввода
        field_params = {"height": 50, "width": 85, "text_align": "center", "content_padding": 5}
        self.dep_input = ft.TextField(label="DEP", **field_params)
        self.arr_input = ft.TextField(label="ARR", **field_params)
        self.altn_input = ft.TextField(label="ALTN", **field_params)

        self.aircraft_select = ft.Dropdown(
            width=220, value="A320CFM", border=ft.InputBorder.NONE,
            options=[ft.dropdown.Option(k) for k in self.aircraft_presets.keys()],
        )

        self.perf_mode_select = ft.Dropdown(
            width=120, value="STD",
            options=[ft.dropdown.Option("ECON"), ft.dropdown.Option("STD"), ft.dropdown.Option("FAST")],
            border_radius=8, dense=True
        )
        
        # Поля для значений
        self.ci_value_field = ft.TextField(
            width=70, height=45, text_align="center", border_radius=8,
            value=str(self.aircraft_presets["A320CFM"]["STD"])
        )
        self.fl_value_field = ft.TextField(width=90, height=45, text_align="center", border_radius=8)
        
        # Текстовые блоки
        self.dist_text = ft.Text("0 nm")
        self.altn_dist_text = ft.Text("0 nm")
        self.time_text = ft.Text("0:00")

        # Привязка событий
        self.aircraft_select.on_select = self._sync_perf_data
        self.perf_mode_select.on_select = self._sync_perf_data
        for f in [self.dep_input, self.arr_input, self.altn_input, self.ci_value_field, self.fl_value_field]:
            f.on_change = self._on_input_change

        # Применить тему и собрать макет
        self._build_ui()

    def _build_ui(self):
        t = self._theme

        # Стили из темы
        EN_STYLE = ft.TextStyle(size=12, weight="bold", color=t.label_en)
        RU_STYLE = ft.TextStyle(size=10, color=t.label_ru)
        VALUE_BIG = ft.TextStyle(size=24, weight="bold", color=t.value)
        VALUE_SMALL = ft.TextStyle(size=16, weight="bold", color=t.value)
        INPUT_STYLE = ft.TextStyle(size=18, weight="bold", color=t.input_text)

        # Применить стили к полям
        for f in [self.dep_input, self.arr_input, self.altn_input, self.ci_value_field, self.fl_value_field]:
            f.text_style = INPUT_STYLE

        self.aircraft_select.text_style = ft.TextStyle(size=16, weight="bold", color=t.input_text)

        self.dist_text.style = VALUE_BIG
        self.altn_dist_text.style = VALUE_SMALL
        self.time_text.style = INPUT_STYLE

        def lang_label(en, ru):
            return ft.Column([ft.Text(en, style=EN_STYLE), ft.Text(ru, style=RU_STYLE)], spacing=0)

        # Контейнер секции
        self.padding = 25
        self.bgcolor = t.card_bg
        self.border_radius = 15
        self.border = ft.border.all(1, t.card_border)
        
        self.content = ft.Column([
            ft.Row([
                ft.Row([
                    ft.Text("FLIGHT PREPARATION / ПОДГОТОВКА", size=15, weight="bold", color=t.title),
                    ft.Container(width=30),
                    self.dep_input, ft.Text("→", size=20, color=t.arrow), 
                    self.arr_input, ft.Text("/", size=20, color=t.arrow), self.altn_input
                ], vertical_alignment="center", spacing=10),
            ]),
            ft.Container(height=20),
            ft.Row([
                ft.Column([
                    ft.Row([lang_label("AIRCRAFT", "САМОЛЁТ"), self.aircraft_select], alignment="spaceBetween"),
                    ft.Divider(height=1, color=t.divider),
                    ft.Row([lang_label("EST TIME", "ВРЕМЯ"), self.time_text], alignment="spaceBetween"),
                    ft.Divider(height=1, color=t.divider),
                    ft.Row([
                        lang_label("COST INDEX", "ИНДЕКС СТОИМОСТИ"), 
                        ft.Row([self.perf_mode_select, self.ci_value_field], spacing=15)
                    ], alignment="spaceBetween"),
                ], expand=3, spacing=15),
                ft.VerticalDivider(width=40, color=t.divider),
                ft.Column([
                    ft.Row([lang_label("DISTANCE", "ДАЛЬНОСТЬ"), self.dist_text], alignment="spaceBetween"),
                    ft.Row([lang_label("ALTN DIST", "ДО ЗАПАСНОГО"), self.altn_dist_text], alignment="spaceBetween"),
                    ft.Divider(height=1, color=t.divider),
                    ft.Row([lang_label("CRUISE FL", "ЭШЕЛОН"), self.fl_value_field], alignment="spaceBetween"),
                ], expand=2, spacing=10)
            ], vertical_alignment="start")
        ])

    def apply_theme(self, theme):
        self._theme = theme
        self._build_ui()
        try:
            self.update()
        except Exception:
            pass

    def _sync_perf_data(self, e):
        """Обновляет Cost Index при смене режима или самолета"""
        ac = self.aircraft_select.value
        mode = self.perf_mode_select.value
        if ac in self.aircraft_presets and mode:
            self.ci_value_field.value = str(self.aircraft_presets[ac][mode])
        self._calculate_logic(None)
        if ac in self.aircraft_presets and mode:
            self.ci_value_field.value = str(self.aircraft_presets[ac][mode])
        try:
            if self.page:
                self.page.update()
        except Exception:
            pass
        if self.on_change_callback:
            self.on_change_callback()

    def _on_input_change(self, e):
        self._calculate_logic(e)
        if self.on_change_callback:
            self.on_change_callback()

    def _calculate_logic(self, e):
        dep = (self.dep_input.value or "").upper().strip()
        arr = (self.arr_input.value or "").upper().strip()
        altn = (self.altn_input.value or "").upper().strip()
        ac_key = self.aircraft_select.value

        if dep in self.airports_data and arr in self.airports_data:
            p1, p2 = self.airports_data[dep], self.airports_data[arr]
            dist = get_distance(p1['LAT'], p1['LON'], p2['LAT'], p2['LON'])
            self.dist_text.value = f"{int(dist)} nm"
            
            bearing = get_bearing(p1['LAT'], p1['LON'], p2['LAT'], p2['LON'])
            going_east = 0 <= bearing < 180

            if dist <= 150:
                auto_fl = "150" if going_east else "160"
            elif dist <= 300:
                auto_fl = "310" if going_east else "320"
            elif dist <= 500:
                auto_fl = "350" if going_east else "360"
            else:
                auto_fl = "390" if going_east else "400"
            
            if not self.fl_value_field.value or (e and e.control in [self.dep_input, self.arr_input]):
                self.fl_value_field.value = auto_fl

            if ac_key and ac_key in self.aircraft_presets:
                base_tas = self.aircraft_presets[ac_key]["TAS"]
                try: ci = int(self.ci_value_field.value or 0)
                except: ci = 0
                gs = base_tas + (ci * 0.12)
                time_m = int((max(0, dist - 50) / gs) * 60) + 18
                self.time_text.value = f"{time_m // 60}:{time_m % 60:02d}"

        if arr in self.airports_data and altn in self.airports_data:
            p_arr, p_altn = self.airports_data[arr], self.airports_data[altn]
            a_dist = get_distance(p_arr['LAT'], p_arr['LON'], p_altn['LAT'], p_altn['LON'])
            self.altn_dist_text.value = f"{int(a_dist)} nm"
        else:
            self.altn_dist_text.value = "0 nm"

        try:
            self.update()
        except Exception:
            pass
