from . import device
import RPi.GPIO as GPIO
import os
import json
import hombit

from flask import abort

class RaspberryPi(device.Device):

    gpio_pins = [ 0, 1, 4, 14, 15, 17, 18, 21, 22, 23, 24, 10, 9, 25, 11, 8, 7 ]

    gpio_modes = {
        GPIO.IN: "in",
        GPIO.OUT: "out"
    }

    def __init__(self, persistent=True):
        device.Device.__init__(self, persistent)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in self.gpio_pins:
            self._pinconfig[str(pin)] = { "mode": "in", "name": None }
            GPIO.setup(pin, GPIO.IN)
        if persistent:
            self.load_from_file();
            for pin in self.gpio_pins:
                self.set_gpio_pin_mode(str(pin))

    def set_io_pins_config(self, pinconfig):
        device.Device.set_io_pins_config(self, pinconfig)
        for pin in pinconfig.keys():
            self.set_gpio_pin_mode(pin)
        return self._pinconfig

    def set_io_pin_config(self, pin, pinconfig):
        device.Device.set_io_pins_config(self, pin, pinconfig)
        self.set_gpio_pin_mode(pin)
        return self._pinconfig[str(pin)]

    def get_io_pins(self):
        pinvalues = {}
        for pin in self.gpio_pins:
            pinvalues[str(pin)] = GPIO.input(pin)
        return pinvalues

    def get_io_pin(self, pin):
        if not pin.isdigit() or not int(pin) in self.gpio_pins:
            abort(404, "invalid pin")
        try:
            return GPIO.input(int(pin))
        except GPIO.WrongDirectionException:
            abort(409, "pin " + pin + " not configured as input")

    def set_io_pin(self, pin, value, hard=False, persist=True):
        if not pin.isdigit() or not int(pin) in self.gpio_pins:
            abort(404, "invalid pin")
        if not hard and self.pin_has_command(pin):
            if not pin in self._pinstate.keys(): self._pinstate[pin] = {}
            self._pinstate[pin]["on"] = value
        if persist and self._persistent: self.save_to_file()
        if hard or not value or not self.pin_has_command(pin):
            try:
                GPIO.output(int(pin), value)
            except GPIO.WrongDirectionException:
                abort(409, "pin " + pin + " not configured as output")

    #

    def set_gpio_pin_mode(self, pin):
        modestr = self._pinconfig[pin]["mode"]
        mode = None
        if modestr == "in": mode = GPIO.IN
        elif modestr == "out": mode = GPIO.OUT
        else: abort(400, "invalid mode (in/out)")
        GPIO.setup(int(pin), mode)


