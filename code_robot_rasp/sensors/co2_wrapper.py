from sensor_wrapper import SensorWrapper
import RPi.GPIO as GPIO
import spidev

spi = spidev.SpiDev()
#spi.open(0,0)

class Co2(SensorWrapper):

    type_ = 'co2'

    def __init__(self, enable, period, type):
        SensorWrapper.__init__(self, enable, period, type)
        GPIO.setmode(GPIO.BOARD)
        self.sensor_pin = 7
        GPIO.setup(self.sensor_pin, GPIO.IN)

    def get_data(self):
        spi.max_speed_hz = 1350000
        adc = spi.xfer2([1,7 << 4, 0])
        lec = ((adc[1]&3) << 8) + adc[2]
        return lec




