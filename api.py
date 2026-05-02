import os
import logging
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

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


def is_api_key_configured() -> bool:
    """Проверяет, задан ли API-ключ CheckWX."""
    return bool(API_KEY and API_KEY.strip())


def fetch_data(url: str):
    if not is_api_key_configured():
        logger.warning("CHECKWX_API_KEY не задан — запрос к %s пропущен", url)
        return None
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 401:
            logger.error("CheckWX API: 401 Unauthorized — неверный или просроченный API-ключ")
            return None
        if r.status_code == 429:
            logger.error("CheckWX API: 429 Too Many Requests — превышен лимит запросов")
            return None
        r.raise_for_status()
        data = r.json()
        if "data" in data and data["data"]:
            return data["data"][0]
        logger.warning("CheckWX API: пустой ответ для %s", url)
    except RequestException as e:
        logger.error("CheckWX API: ошибка сети — %s", e)
    except ValueError as e:
        logger.error("CheckWX API: ошибка парсинга JSON — %s", e)
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
    raw = fetch_data(f"https://api.checkwx.com/v2/metar/{icao}")
    return raw if raw else "Нет данных"


# ---------- RAW TAF (fallback) ----------
def get_taf_raw(icao: str):
    icao = icao.upper().strip()
    if not icao:
        return "Нет данных"
    raw = fetch_data(f"https://api.checkwx.com/v2/taf/{icao}")
    return raw if raw else "Нет данных"
