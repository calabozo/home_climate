import RPi.GPIO as GPIO


VENT_GPIO = [2,3,14,15]
VENT_OPEN = GPIO.HIGH
VENT_CLOSE = GPIO.LOW

def open_vent(vent_id: int):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(VENT_GPIO[vent_id], GPIO.OUT)
    GPIO.output(VENT_GPIO[vent_id], VENT_OPEN)
    

def close_vent(vent_id: int):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(VENT_GPIO[vent_id], GPIO.OUT)
    GPIO.output(VENT_GPIO[vent_id], VENT_CLOSE)
    
    