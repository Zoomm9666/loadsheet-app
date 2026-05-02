# data/aircraft_db.py

class Aircraft:
    def __init__(self, name, fuel_burn_kgph, oew_kg, mtow_kg=78000, mldw_kg=66000, mzfw_kg=62000, taxi_fuel_kg=200, apu_fuel_kg=60):
        self.name = name
        self.fuel_burn_kgph = fuel_burn_kgph
        self.oew_kg = oew_kg
        self.mtow_kg = mtow_kg
        self.mldw_kg = mldw_kg
        self.mzfw_kg = mzfw_kg
        self.taxi_fuel_kg = taxi_fuel_kg
        self.apu_fuel_kg = apu_fuel_kg

AIRCRAFT_TYPES = {
    "A319":     Aircraft("A319", 2300, 41374, mtow_kg=70000, mldw_kg=61000, mzfw_kg=57000),
    "A320CFM":  Aircraft("A320CFM", 2400, 42600, mtow_kg=78000, mldw_kg=66000, mzfw_kg=62000),
    "A320IAE":  Aircraft("A320IAE", 2450, 43000, mtow_kg=78000, mldw_kg=66000, mzfw_kg=62000),
    "A320NEO":  Aircraft("A320NEO", 2200, 44500, mtow_kg=79000, mldw_kg=67000, mzfw_kg=63000),
    "A321":     Aircraft("A321", 2600, 47500, mtow_kg=97000, mldw_kg=78000, mzfw_kg=73500, taxi_fuel_kg=250, apu_fuel_kg=70),
    "B737-700": Aircraft("B737-700", 2400, 38147, mtow_kg=70080, mldw_kg=58604, mzfw_kg=54600),
    "B737-800": Aircraft("B737-800", 2600, 41413, mtow_kg=79016, mldw_kg=65317, mzfw_kg=61600),
    "B737-900": Aircraft("B737-900", 2700, 44676, mtow_kg=85130, mldw_kg=71321, mzfw_kg=65700, taxi_fuel_kg=250, apu_fuel_kg=70),
}
