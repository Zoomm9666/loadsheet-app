import os
import base64
import flet as ft
from ui.theme import AppTheme
from ui.flight_section import FlightCard
from ui.loading_section import LoadingCard
from ui.fuel_section import FuelCard
from ui.weather_section import WeatherCard
from data.aircraft_db import AIRCRAFT_TYPES
from core.fuel_logic import calc_fuel
from core.loadsheet_generator import generate_loadsheet

def main(page: ft.Page):
    # Настройки страницы
    page.title = "Aviation Loadsheet Pro"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # ── Режим запуска (веб / десктоп) ─────────────────────────
    is_web = os.environ.get("PORT") is not None

    # ── Тема (тёмная по умолчанию) ────────────────────────────
    theme = AppTheme(is_dark=True)

    def apply_page_theme():
        page.bgcolor = theme.page_bg
        page.theme_mode = theme.flet_theme_mode
        page.theme = theme.flet_theme()
        page.update()

    apply_page_theme()

    # 1. Инициализация компонентов
    flight = FlightCard(on_change_callback=lambda: update_all(), _theme=theme)
    loading = LoadingCard(on_change_callback=lambda: update_all(), _theme=theme)
    fuel = FuelCard(on_change_callback=lambda: update_all(), _theme=theme)
    weather = WeatherCard(flight, _theme=theme)

    # ── Переключатель темы ─────────────────────────────────────
    theme_switch = ft.Switch(
        label="🌙 DARK",
        value=True,
        on_change=lambda e: toggle_theme(),
    )

    def toggle_theme():
        theme.toggle()
        theme_switch.label = "🌙 DARK" if theme.is_dark else "☀️ LIGHT"
        theme_switch.value = theme.is_dark
        apply_page_theme()
        flight.apply_theme(theme)
        loading.apply_theme(theme)
        fuel.apply_theme(theme)
        weather.apply_theme(theme)
        page.update()

    # ── Собрать все данные для loadsheet ───────────────────────
    def collect_data():
        """Собирает все текущие данные из UI в один словарь для PDF."""
        try:
            ac_key = flight.aircraft_select.value or "A320CFM"
            ac = AIRCRAFT_TYPES[ac_key]

            # Дистанции
            dist_str = flight.dist_text.value.replace(" nm", "").replace("\u202f", "")
            dist = float(dist_str) if dist_str not in ("---", "0", "") else 0

            altn_str = flight.altn_dist_text.value.replace(" nm", "").replace("\u202f", "")
            altn_dist = float(altn_str) if altn_str not in ("---", "0", "") else 0

            # Ground Speed
            try:
                ci = int(flight.ci_value_field.value or 0)
            except ValueError:
                ci = 0
            base_tas = flight.aircraft_presets.get(ac_key, {}).get("TAS", 450)
            gs = base_tas + (ci * 0.12)

            # Payload
            load_data = loading.get_payload_data()
            payload_total = load_data['total_kg']

            # Fuel params
            try:
                extra_kg = float(fuel.extra_input.value or 0)
            except ValueError:
                extra_kg = 0
            try:
                hold_min = int(fuel.hold_input.value or 30)
            except ValueError:
                hold_min = 30
            try:
                taxi_kg = float(fuel.taxi_input.value or 200)
            except ValueError:
                taxi_kg = 200
            try:
                apu_kg = float(fuel.apu_input.value or 60)
            except ValueError:
                apu_kg = 60
            ice_on = fuel.ice_switch.value

            # Fuel calculation
            fuel_data = calc_fuel(
                distance_nm=dist,
                gs_kts=gs,
                aircraft=ac,
                alternate_nm=altn_dist,
                extra_kg=extra_kg,
                hold_minutes=hold_min,
                ice_on=ice_on,
                taxi_kg=taxi_kg,
                apu_kg=apu_kg,
            )

            # Weights
            zfw = ac.oew_kg + payload_total
            tow = zfw + fuel_data["block_fuel"]
            lw = tow - fuel_data["trip_fuel"]

            return {
                "flight": {
                    "dep": (flight.dep_input.value or "").upper(),
                    "arr": (flight.arr_input.value or "").upper(),
                    "altn": (flight.altn_input.value or "").upper(),
                    "distance": flight.dist_text.value or "0 nm",
                    "altn_distance": flight.altn_dist_text.value or "0 nm",
                    "time": flight.time_text.value or "0:00",
                    "fl": flight.fl_value_field.value or "—",
                    "ci": ci,
                    "gs": round(gs),
                },
                "aircraft": {
                    "name": ac.name,
                    "fuel_burn": ac.fuel_burn_kgph,
                    "oew": ac.oew_kg,
                    "mtow": ac.mtow_kg,
                    "mldw": ac.mldw_kg,
                    "mzfw": ac.mzfw_kg,
                },
                "payload": {
                    "adult": load_data.get("adult", 0),
                    "child": load_data.get("child", 0),
                    "inf": load_data.get("inf", 0),
                    "total_pax": load_data.get("total_pax", 0),
                    "pax_weight": load_data.get("pax_weight", 0),
                    "hand_lug": load_data.get("hand_luggage_weight", 0) // 8 if load_data.get("hand_luggage_weight", 0) else 0,
                    "hand_luggage_weight": load_data.get("hand_luggage_weight", 0),
                    "bag_count": load_data.get("bag_total", 0) // int(loading.bag_weight_dropdown.value or 20) if load_data.get("bag_total", 0) else 0,
                    "bag_weight": int(loading.bag_weight_dropdown.value or 20),
                    "bag_total": load_data.get("bag_total", 0),
                    "captain": load_data.get("adult", 0) and 1,  # approximate
                    "fo": load_data.get("adult", 0) and 1,
                    "fa": 0,
                    "crew_bag": 0,
                    "crew_weight": load_data.get("crew_weight", 0),
                    "catering_weight": load_data.get("catering_weight", 0),
                    "water": load_data.get("water", 0),
                    "cargo": load_data.get("cargo", 0),
                    "mail": load_data.get("mail", 0),
                    "total_kg": payload_total,
                },
                "fuel": {
                    "trip_fuel": fuel_data["trip_fuel"],
                    "trip_time": fuel_data["trip_time"],
                    "contingency": fuel_data["contingency"],
                    "reserve_fuel": fuel_data["reserve_fuel"],
                    "final_time": fuel_data["final_time"],
                    "alt_fuel": fuel_data["alt_fuel"],
                    "alt_time": fuel_data["alt_time"],
                    "taxi_fuel": fuel_data["taxi_fuel"],
                    "apu_fuel": fuel_data["apu_fuel"],
                    "hold_fuel": fuel_data["hold_fuel"],
                    "hold_time": fuel_data["hold_time"],
                    "ice_penalty": fuel_data["ice_penalty"],
                    "extra_fuel": fuel_data["extra_fuel"],
                    "block_fuel": fuel_data["block_fuel"],
                    "ice_on": ice_on,
                },
                "weights": {
                    "oew": ac.oew_kg,
                    "payload": payload_total,
                    "zfw": zfw,
                    "mzfw": ac.mzfw_kg,
                    "tow": tow,
                    "mtow": ac.mtow_kg,
                    "lw": lw,
                    "mldw": ac.mldw_kg,
                },
            }
        except Exception as e:
            print(f"Data collection error: {e}")
            return None

    # ── Вспомогательная: открыть/скачать PDF ────────────────────
    def _open_pdf(pdf_path):
        """Открывает PDF кросс-платформенно: десктоп — локально, веб — data URL."""
        if is_web:
            # В веб-режиме кодируем PDF в base64 и открываем как data URL
            with open(pdf_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            data_url = f"data:application/pdf;base64,{b64}"
            page.launch_url(data_url)
        else:
            page.launch_url(pdf_path)

    # ── Генерация и открытие Loadsheet PDF ─────────────────────
    def open_loadsheet(e):
        data = collect_data()
        if not data:
            return

        try:
            pdf_path = generate_loadsheet(data)
            _open_pdf(pdf_path)
        except Exception as ex:
            import traceback
            traceback.print_exc()

    # ── Сохранение PDF с выбором пути ─────────────────────────
    def download_loadsheet(e):
        data = collect_data()
        if not data:
            return

        # Десктоп: попробовать tkinter диалог выбора пути
        if not is_web:
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                ac_name = flight.aircraft_select.value or "A320"
                dep = (flight.dep_input.value or "DEP").upper()
                arr = (flight.arr_input.value or "ARR").upper()
                default_name = f"loadsheet_{ac_name}_{dep}_{arr}.pdf"
                save_path = filedialog.asksaveasfilename(
                    title="Save Loadsheet PDF",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=default_name,
                )
                root.destroy()
                if save_path:
                    generate_loadsheet(data, save_path)
                    page.launch_url(save_path)
                return
            except Exception:
                pass

        # Веб-режим или tkinter недоступен: открыть через data URL
        try:
            pdf_path = generate_loadsheet(data)
            _open_pdf(pdf_path)
        except Exception as ex:
            import traceback
            traceback.print_exc()

    # ── Кнопка LOADSHEET ───────────────────────────────────────
    loadsheet_btn = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.DESCRIPTION, color="white", size=24),
            ft.Text("LOADSHEET", size=18, weight="bold", color="white"),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        bgcolor="#1E40AF",
        color="white",
        height=55,
        width=280,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            elevation=4,
        ),
        on_click=open_loadsheet,
    )

    download_btn = ft.OutlinedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.SAVE, size=20),
            ft.Text("SAVE PDF", size=14, weight="bold"),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        height=45,
        width=180,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            side=ft.BorderSide(2, theme.accent),
        ),
        on_click=download_loadsheet,
    )

    def update_all():
        """Главная функция расчётов, вызываемая при любом изменении ввода"""
        try:
            # Получаем выбранный тип самолёта
            ac_key = flight.aircraft_select.value
            if not ac_key:
                return

            # Данные самолёта из БД
            ac = AIRCRAFT_TYPES[ac_key]

            # Получаем дистанцию маршрута
            dist_str = flight.dist_text.value.replace(" nm", "").replace("\u202f", "")
            dist = float(dist_str) if dist_str not in ("---", "0", "") else 0

            # Получаем дистанцию до запасного
            altn_str = flight.altn_dist_text.value.replace(" nm", "").replace("\u202f", "")
            altn_dist = float(altn_str) if altn_str not in ("---", "0", "") else None

            # Ground Speed (TAS + CI коррекция, как в flight_section)
            try:
                ci = int(flight.ci_value_field.value or 0)
            except ValueError:
                ci = 0
            base_tas = flight.aircraft_presets.get(ac_key, {}).get("TAS", 450)
            gs = base_tas + (ci * 0.12)

            # Данные о загрузке (PAX + Cargo)
            load_data = loading.get_payload_data()
            payload_total = load_data['total_kg']

            # Параметры топлива из FuelCard
            try:
                extra_kg = float(fuel.extra_input.value or 0)
            except ValueError:
                extra_kg = 0

            try:
                hold_min = int(fuel.hold_input.value or 30)
            except ValueError:
                hold_min = 30

            try:
                taxi_kg = float(fuel.taxi_input.value or 200)
            except ValueError:
                taxi_kg = 200

            try:
                apu_kg = float(fuel.apu_input.value or 60)
            except ValueError:
                apu_kg = 60

            ice_on = fuel.ice_switch.value

            # Время полёта из первого блока
            flight_time_str = flight.time_text.value or "0:00"

            # ═══ РАСЧЁТ ТОПЛИВА ═══
            fuel_data = calc_fuel(
                distance_nm=dist,
                gs_kts=gs,
                aircraft=ac,
                alternate_nm=altn_dist,
                extra_kg=extra_kg,
                hold_minutes=hold_min,
                ice_on=ice_on,
                taxi_kg=taxi_kg,
                apu_kg=apu_kg,
            )

            # ═══ РАСЧЁТ ВЕСОВ ═══
            # Zero Fuel Weight = OEW + Payload
            zfw = ac.oew_kg + payload_total

            # Take-Off Weight = ZFW + Block Fuel
            tow = zfw + fuel_data["block_fuel"]

            # Landing Weight = TOW - Trip Fuel
            lw = tow - fuel_data["trip_fuel"]

            # ═══ ОБНОВЛЕНИЕ ИНТЕРФЕЙСА ═══
            fuel.update_ui(
                fuel_data=fuel_data,
                tow=tow,
                lw=lw,
                mtow=ac.mtow_kg,
                mldw=ac.mldw_kg,
                flight_time_str=flight_time_str,
                oew=ac.oew_kg,
                payload=payload_total,
                zfw=zfw,
                mzfw=ac.mzfw_kg,
            )

            page.update()

        except Exception as e:
            import traceback
            traceback.print_exc()

    # Сборка макета
    page.add(
        ft.Column([
            # Заголовок + переключатель темы
            ft.Row([
                ft.Text("✈️", size=30),
                ft.Text("LOADSHEET APP", size=28, weight="bold", color=theme.accent),
                ft.Container(expand=True),
                theme_switch,
            ]),

            ft.Divider(height=10, color="transparent"),

            # Блок подготовки полёта
            flight,

            # Блок загрузки (Passengers / Cargo)
            loading,

            # Блок расчёта заправки топливом
            fuel,

            # Блок погоды (METAR / TAF)
            weather,

            ft.Divider(height=20, color="transparent"),

            # ── Кнопка LOADSHEET ──
            ft.Row([
                loadsheet_btn,
                download_btn,
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),

            ft.Container(height=20),

        ], spacing=25)
    )

    page.update()

    # Начальный расчёт при запуске
    update_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Определяем режим: если есть PORT env — веб, иначе десктоп
    is_web = os.environ.get("PORT") is not None
    if is_web:
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port, host="0.0.0.0")
    else:
        ft.app(target=main)
