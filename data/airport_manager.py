import pandas as pd
import os
import sys

# Исправление кодировки для Windows-консоли
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def load_airports():
    """Загружает базу из airports.csv с фиксированными именами колонок."""
    csv_path = "data/airports.csv"
    
    if not os.path.exists(csv_path):
        print(f"ERROR: File {csv_path} not found!")
        return {}

    try:
        # Читаем CSV
        df = pd.read_csv(csv_path, sep=',', engine='python')

        # Приводим названия колонок к единому стандарту (UPPERCASE)
        df.columns = [c.strip().upper() for c in df.columns]

        # Твои реальные колонки из файла:
        column_map = {
            'ICAO_CODE': 'ICAO',
            'LATITUDE_DEG': 'LAT',
            'LONGITUDE_DEG': 'LON'
        }

        # Проверка: все ли нужные колонки есть в наличии
        for key in column_map.keys():
            if key not in df.columns:
                print(f"ERROR: Column '{key}' not found in airports.csv")
                print(f"Available columns: {df.columns.tolist()}")
                return {}

        # Переименовываем колонки для логики приложения
        df = df.rename(columns=column_map)
        
        # Убираем строки без кода аэропорта и преобразуем в верхний регистр
        df = df.dropna(subset=['ICAO'])
        df['ICAO'] = df['ICAO'].astype(str).str.upper().str.strip()
        
        # Создаем словарь для быстрого поиска: { 'ULLI': {'LAT': 59.8, 'LON': 30.2}, ... }
        airports_dict = df.set_index('ICAO')[['LAT', 'LON']].to_dict('index')
        
        print(f"DB READY: Loaded {len(airports_dict)} airports.")
        return airports_dict

    except Exception as e:
        print(f"Critical error reading DB: {e}")
        return {}

def sync_airports():
    """Функция-обертка для вызова из main.py"""
    return load_airports()