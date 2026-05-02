import os
import requests
from requests.exceptions import RequestException

# ── Автозагрузка .env файла ────────────────────────────────────
# Читает файл .env из корня проекта и устанавливает переменные окружения
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path, encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _, _val = _line.partition("=")
                _key = _key.strip()
                _val = _val.strip()
                if _key and _key not in os.environ:
                    os.environ[_key] = _val

# API-ключ берётся из переменной окружения CHECKWX_API_KEY
# Значение можно задать: 1) в файле .env  2) через set CHECKWX_API_KEY=...  3) в Docker через -e
API_KEY = os.environ.get("CHECKWX_API_KEY", "")

HEADERS = {
    "X-API-Key": API_KEY,
    "Accept": "application/json"
}


def fetch_data(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        r.raise_for_status()
        data = r.json()
        if "data" in data and data["data"]:
            return data["data"][0]
    except (RequestException, ValueError):
        pass
    return None


# ---------- DECODED METAR ----------
def get_metar(icao: str):
    icao = icao.upper().strip()
    if not icao:
        return None
    return fetch_data(f"https://api.checkwx.com/v2/metar/{icao}/decoded")


# ---------- DECODED TAF ----------
def get_taf(icao: str):
    icao = icao.upper().strip()
    if not icao:
        return None
    return fetch_data(f"https://api.checkwx.com/v2/taf/{icao}/decoded")


# ---------- RAW METAR (fallback) ----------
def get_metar_raw(icao: str):
    icao = icao.upper().strip()
    if not icao:
        return "Нет данных"
    raw = fetch_data(f"https://api.checkwx.com/metar/{icao}")
    return raw if raw else "Нет данных"


# ---------- RAW TAF (fallback) ----------
def get_taf_raw(icao: str):
    icao = icao.upper().strip()
    if not icao:
        return "Нет данных"
    raw = fetch_data(f"https://api.checkwx.com/taf/{icao}")
    return raw if raw else "Нет данных"
