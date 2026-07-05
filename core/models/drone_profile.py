from dataclasses import dataclass

@dataclass
class DroneProfile:
    weight_grams: int
    prop_size_inches: float
    motor_kv: int
