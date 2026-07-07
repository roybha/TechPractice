import pandas as pd
import os
from core.models.flight import FlightData

class LogParser:
    def __init__(self):
        self.axis_names: dict = {
            "time": ["time", "time (us)", "loopIteration", "timestamp", "TimeUS", "sys_time"],
            "gyro_roll": ["gyroADC[0]", "gyroRoll", "gyro_roll", "roll", "GyrX", "GYR.GyrX"],
            "gyro_pitch": ["gyroADC[1]", "gyroPitch", "gyro_pitch", "pitch", "GyrY", "GYR.GyrY"],
            "gyro_yaw": ["gyroADC[2]", "gyroYaw", "gyro_yaw", "yaw", "GyrZ", "GYR.GyrZ"],
            "setpoint_roll": ["setpoint[0]", "rcCommand[0]", "rcRoll", "rc_roll", "setpoint_roll", "DesRoll", "PIDR.Tar"],
            "setpoint_pitch": ["setpoint[1]", "rcCommand[1]", "rcPitch", "rc_pitch", "setpoint_pitch", "DesPitch", "PIDP.Tar"],
            "setpoint_yaw": ["setpoint[2]", "rcCommand[2]", "rcYaw", "rc_yaw", "setpoint_yaw", "DesYaw", "PIDY.Tar"]
        }
    def parse(self, filepath: str):
        if not filepath.endswith(".csv"):
            raise ValueError("File extension must be .csv")

        try:
            data_frame = pd.read_csv(filepath)
            clean_df = self._extract_columns(data_frame)
            time_array = clean_df["time"].to_numpy()
            duration_seconds = (time_array[-1] - time_array[0]) / 1_000_000.0

            sample_rate_hz = len(time_array) / duration_seconds if duration_seconds > 0 else 0.0

            return FlightData(
                filename=os.path.basename(filepath),
                duration_seconds=duration_seconds,
                sample_rate_hz=sample_rate_hz,
                timestamp=time_array,
                gyro_roll=clean_df["gyro_roll"].to_numpy(),
                gyro_pitch=clean_df["gyro_pitch"].to_numpy(),
                gyro_yaw=clean_df["gyro_yaw"].to_numpy(),
                setpoint_roll=clean_df["setpoint_roll"].to_numpy(),
                setpoint_pitch=clean_df["setpoint_pitch"].to_numpy(),
                setpoint_yaw=clean_df["setpoint_yaw"].to_numpy()
            )
        except FileNotFoundError:
            raise FileNotFoundError("File not found")

    def _extract_columns(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        extracted_df = pd.DataFrame()

        for target_name, synonyms in self.axis_names.items():

            column_found = False
            for synonym in synonyms:
                if synonym in data_frame.columns:
                    extracted_df[target_name] = data_frame[synonym]
                    column_found = True
                    break

            if not column_found:
                raise ValueError(f"Column for axes {target_name} not found")

        return extracted_df