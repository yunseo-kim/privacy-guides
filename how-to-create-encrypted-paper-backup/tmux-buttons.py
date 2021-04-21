import RPi.GPIO as GPIO
import keyboard
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def click(channel):
  if channel == 17:
    keyboard.send("ctrl+b, up")
  elif channel == 22:
    keyboard.send("ctrl+b, down")
  elif channel == 23:
    keyboard.send("ctrl+b, shift+7")
  # elif channel == 27:
  #   keyboard.send("")
GPIO.add_event_detect(17, GPIO.RISING, callback=click, bouncetime=300)
GPIO.add_event_detect(22, GPIO.RISING, callback=click, bouncetime=300)
GPIO.add_event_detect(23, GPIO.RISING, callback=click, bouncetime=300)
# GPIO.add_event_detect(27, GPIO.RISING, callback=click, bouncetime=300)

while True:
  time.sleep(60)

GPIO.cleanup()
