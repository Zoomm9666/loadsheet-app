# ui/theme.py
"""Централизованная палитра цветов для тёмной и светлой темы."""


class AppTheme:
    """Цветовая палитра приложения. is_dark=True — тёмная тема (по умолчанию)."""

    def __init__(self, is_dark=True):
        self.is_dark = is_dark
        self._apply()

    def toggle(self):
        self.is_dark = not self.is_dark
        self._apply()

    def _apply(self):
        d = self.is_dark

        # ── Страница ──────────────────────────────────────────
        self.page_bg = "#0F172A" if d else "#F0F2F5"

        # ── Карточки (секции) ─────────────────────────────────
        self.card_bg = "#1E293B" if d else "#F8FAFC"
        self.card_border = "#334155" if d else "#D0D7DE"
        self.card_border_width = 1

        # ── Разделители ───────────────────────────────────────
        self.divider = "#475569" if d else "#E1E4E8"

        # ── Тексты ────────────────────────────────────────────
        self.title = "#E2E8F0" if d else "#404B69"          # заголовки секций
        self.label_en = "#94A3B8" if d else "#505F79"       # английские метки
        self.label_ru = "#64748B" if d else "#7A869A"       # русские метки
        self.section_title = "#94A3B8" if d else "#6B7280"  # подразделы
        self.value = "#60A5FA" if d else "#1D4ED8"          # значения (синий)
        self.accent = "#F59E0B" if d else "#D97706"         # акцент (оранжевый)
        self.input_text = "#F1F5F9" if d else "#000000"     # текст ввода
        self.arrow = "#64748B" if d else "#9CA3AF"          # стрелки, плюсы

        # ── Лимиты ────────────────────────────────────────────
        self.limit_ok = "#64748B" if d else "#9CA3AF"       # лимит в норме
        self.limit_warn = "#F87171" if d else "#C62828"     # превышение

        # ── Индикация веса: ЗЕЛЁНЫЙ (норма) ──────────────────
        self.green_bg = "#052E16" if d else "#E8F5E9"
        self.green_border = "#16A34A" if d else "#4CAF50"
        self.green_text = "#4ADE80" if d else "#2E7D32"

        # ── Индикация веса: КРАСНЫЙ (превышение) ─────────────
        self.red_bg = "#450A0A" if d else "#FFEBEE"
        self.red_border = "#DC2626" if d else "#F44336"
        self.red_text = "#F87171" if d else "#C62828"

        # ── Блок итога (Block Fuel / Total Payload) ──────────
        self.total_bg = "#451A03" if d else "#FFFBEB"
        self.total_border = "#F59E0B" if d else "#D97706"

        # ── Поля ввода ────────────────────────────────────────
        self.input_bg = "#0F172A" if d else "#FFFFFF"
        self.input_border = "#475569" if d else "#D0D7DE"
        self.input_border_focus = "#60A5FA" if d else "#1D4ED8"

        # ── Погода (внутренние панели) ────────────────────────
        self.weather_card_bg = "#0F172A" if d else "#1E293B"
        self.weather_panel_bg = "#020617" if d else "#0F172A"
        self.weather_text = "#E2E8F0" if d else "#F1F5F9"
        self.weather_border = "#374151" if d else "#4B5563"

        # ── Переключатель ─────────────────────────────────────
        self.switch_label = "#94A3B8" if d else "#505F79"

    @property
    def flet_theme_mode(self):
        import flet as ft
        return ft.ThemeMode.DARK if self.is_dark else ft.ThemeMode.LIGHT

    def flet_theme(self):
        """Возвращает объект ft.Theme для настройки виджетов Flet."""
        import flet as ft
        if self.is_dark:
            return ft.Theme(
                color_scheme=ft.ColorScheme(
                    surface="#1E293B",
                    on_surface="#E2E8F0",
                    primary="#60A5FA",
                    on_primary="#FFFFFF",
                    secondary="#F59E0B",
                    on_secondary="#000000",
                    error="#F87171",
                    on_error="#000000",
                )
            )
        else:
            return ft.Theme(
                color_scheme=ft.ColorScheme(
                    surface="#F8FAFC",
                    on_surface="#1E293B",
                    primary="#1D4ED8",
                    on_primary="#FFFFFF",
                    secondary="#D97706",
                    on_secondary="#FFFFFF",
                    error="#C62828",
                    on_error="#FFFFFF",
                )
            )
