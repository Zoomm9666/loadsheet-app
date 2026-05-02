# core/fuel_logic.py

def calc_fuel(
    distance_nm,
    gs_kts,
    aircraft,
    alternate_nm=None,
    extra_kg=800,
    hold_minutes=None,
    ice_on=False,
    taxi_kg=None,
    apu_kg=None,
):
    """
    Полный авиационный расчёт топлива по нормам ICAO/EASA.
    Все расчёты ведутся в КИЛОГРАММАХ.
    """
    burn_kgph = aircraft.fuel_burn_kgph
    burn_per_min = burn_kgph / 60

    # Trip
    trip_time_hours = distance_nm / gs_kts
    trip_fuel = trip_time_hours * burn_kgph
    trip_time_min = trip_time_hours * 60

    # Contingency (5% или минимум 5 минут)
    contingency_5_percent = trip_fuel * 0.05
    contingency_min_5min = burn_per_min * 5
    contingency = max(contingency_5_percent, contingency_min_5min)

    # Final Reserve (30 минут)
    final_reserve = burn_per_min * 30
    final_time = 30

    # Alternate (реалистичная формула: climb + cruise + descent)
    if alternate_nm is None or alternate_nm == 0:
        alternate_nm = 100

    alt_time_hours = alternate_nm / gs_kts
    alt_cruise_fuel = alt_time_hours * burn_kgph

    alt_climb_fuel = 400     # среднее для A320 family
    alt_descent_fuel = 200   # среднее для A320 family

    alt_fuel = alt_cruise_fuel + alt_climb_fuel + alt_descent_fuel
    alt_time = alt_time_hours * 60

    # Taxi (если не указано — берём из БД самолёта)
    taxi_fuel = float(taxi_kg) if taxi_kg is not None else aircraft.taxi_fuel_kg

    # APU (если не указано — берём из БД самолёта)
    apu_fuel = float(apu_kg) if apu_kg is not None else aircraft.apu_fuel_kg

    # HOLD
    if hold_minutes is None or hold_minutes == "":
        hold_minutes = 30
    hold_minutes = int(hold_minutes)
    hold_fuel = burn_per_min * hold_minutes

    # ICE
    ice_penalty = trip_fuel * 0.10 if ice_on else 0

    # Extra
    extra_fuel = float(extra_kg) if extra_kg else 0

    # Block
    block_fuel = (
        trip_fuel
        + contingency
        + final_reserve
        + alt_fuel
        + taxi_fuel
        + apu_fuel
        + hold_fuel
        + ice_penalty
        + extra_fuel
    )

    return {
        "trip_fuel": round(trip_fuel),
        "contingency": round(contingency),
        "reserve_fuel": round(final_reserve),
        "alt_fuel": round(alt_fuel),
        "taxi_fuel": round(taxi_fuel),
        "apu_fuel": round(apu_fuel),
        "hold_fuel": round(hold_fuel),
        "ice_penalty": round(ice_penalty),
        "extra_fuel": round(extra_fuel),
        "block_fuel": round(block_fuel),

        "trip_time": round(trip_time_min),
        "alt_time": round(alt_time),
        "final_time": final_time,
        "hold_time": hold_minutes,
    }
