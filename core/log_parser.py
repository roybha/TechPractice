class LogParser:
    def __init__(self):
        axis_names: dict = {
            "time": ["time", "time (us)", "loopIteration", "timestamp", "TimeUS", "sys_time"],
            "gyro_roll": ["gyroADC[0]", "gyroRoll", "gyro_roll", "roll", "GyrX", "GYR.GyrX"],
            "gyro_pitch": ["gyroADC[1]", "gyroPitch", "gyro_pitch", "pitch", "GyrY", "GYR.GyrY"],
            "gyro_yaw": ["gyroADC[2]", "gyroYaw", "gyro_yaw", "yaw", "GyrZ", "GYR.GyrZ"],
            "setpoint_roll": ["setpoint[0]", "rcCommand[0]", "rcRoll", "rc_roll", "setpoint_roll", "DesRoll", "PIDR.Tar"],
            "setpoint_pitch": ["setpoint[1]", "rcCommand[1]", "rcPitch", "rc_pitch", "setpoint_pitch", "DesPitch", "PIDP.Tar"],
            "setpoint_yaw": ["setpoint[2]", "rcCommand[2]", "rcYaw", "rc_yaw", "setpoint_yaw", "DesYaw", "PIDY.Tar"]
        }
    def parse(self, filepath: str):
        pass