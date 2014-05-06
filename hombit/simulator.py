from . import device
import os
import json
import hombit


class Simulator(device.Device):
    _pins = {}

    def __init__(self, numPins=30, persistent=True):
        device.Device.__init__(self, persistent)
        for i in range(numPins):
            self._pins[str(i)] = False
            self._pinconfig[str(i)] = {"mode": "in", "name": None}
        if persistent:
            self.load_from_file();

    def get_io_pins(self):
        return self._pins

    def get_io_pin(self, pin):
        return self._pins[pin]

    def set_io_pin(self, pin, value, hard=False, persist=True):
        if not pin in self._pins:
            raise KeyError(pin + " is not a valid pin")
        if not hard and self.pin_has_command(pin):
            if not pin in self._pinstate.keys(): self._pinstate[pin] = {}
            self._pinstate[pin]["on"] = value
        if persist and self._persistent: self.save_to_file()
        if hard or not value or not self.pin_has_command(pin):
            self._pins[pin] = value

    #

    def read_config(self, config):
        self._pins = config["pins"]
        return config

    def write_config(self, config):
        config.update({
            "pins": self._pins
        })
        return config
