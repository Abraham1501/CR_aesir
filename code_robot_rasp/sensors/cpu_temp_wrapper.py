from sensor_wrapper import SensorWrapper
from gpiozero import CPUTemperature


class CPUTempWrapper(SensorWrapper):
    # What type of sensor this wrapper handles
    type_ = 'cpu_temp'

    def __init__(self, enable, period, type):
        SensorWrapper.__init__(self, enable, period, type)

    def get_data(self):
        
        cpu = CPUTemperature()
        return cpu.temperature