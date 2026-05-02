import math

def get_distance(lat1, lon1, lat2, lon2):
    """
    Вычисляет расстояние между двумя точками на Земле в морских милях (NM).
    """
    try:
        # Переводим координаты в радианы
        phi1, lam1 = math.radians(lat1), math.radians(lon1)
        phi2, lam2 = math.radians(lat2), math.radians(lon2)
        
        # Формула гаверсинусов
        dphi = phi2 - phi1
        dlam = lam2 - lam1
        
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        # Радиус Земли в морских милях
        radius_nm = 3440.065
        
        return c * radius_nm
    except Exception as e:
        print(f"Distance calc error: {e}")
        return 0


def get_bearing(lat1, lon1, lat2, lon2):
    """
    Вычисляет начальный азимут (bearing) от точки 1 к точке 2 в градусах (0-360).
    0° = север, 90° = восток, 180° = юг, 270° = запад.
    Используется для определения направления полёта (восток/запад)
    и выбора эшелона по полукруговой схеме ICAO.
    """
    try:
        phi1, lam1 = math.radians(lat1), math.radians(lon1)
        phi2, lam2 = math.radians(lat2), math.radians(lon2)
        
        dlam = lam2 - lam1
        
        x = math.sin(dlam) * math.cos(phi2)
        y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
        
        bearing = math.degrees(math.atan2(x, y))
        # Нормализуем в диапазон 0-360
        return (bearing + 360) % 360
    except Exception as e:
        print(f"Bearing calc error: {e}")
        return 0