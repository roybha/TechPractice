from dataclasses import dataclass
import numpy as np

@dataclass
class FlightData:
    # Metadata of files
    filename: str
    duration_seconds: float
    sample_rate_hz: float

    # Time from a flight's start
    timestamp: np.ndarray

    gyro_roll: np.ndarray
    gyro_pitch: np.ndarray
    gyro_yaw: np.ndarray

    setpoint_roll: np.ndarray
    setpoint_pitch: np.ndarray
    setpoint_yaw: np.ndarray