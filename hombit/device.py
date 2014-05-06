import string
import random
import os
import time
import hombit
import json


class Device:
    _pinconfig = {}
    _pinstate = {}
    _commandstate = {}
    _persistent = False

    min_command_interval = 1

    def __init__(self, persistent=True):
        self._persistent = persistent
        self.generate_random_id()

    def generate_random_id(self, size=6, chars=string.ascii_uppercase + string.digits):
        self._id = "".join(random.choice(chars) for x in range(size))

    def get_device_type(self):
        return self.__class__.__name__

    def get_device_id(self):
        return self._id

    def set_device_id(self, id):
        self._id = id
        if self._persistent: self.save_to_file()

    def get_io_pins_config(self):
        return self._pinconfig

    def set_io_pins_config(self, pinconfig):
        for pin in pinconfig.keys():
            self._pinconfig[pin].update(pinconfig[pin])
        if self._persistent: self.save_to_file()
        return self._pinconfig

    def get_io_pin_config(self, pin):
        return self._pinconfig[pin];

    def set_io_pin_config(self, pin, pinconfig):
        self._pinconfig[pin].update(pinconfig)
        if self._persistent: self.save_to_file()
        return pinconfig

    def get_named_io_pin_config(self, name):
        pin = self.get_pin_by_name(name)
        if not pin: raise KeyError(name + " not found")
        return self._pinconfig[pin];

    def set_named_io_pin_config(self, name, pinconfig):
        pin = self.get_pin_by_name(name)
        if not pin: raise KeyError(name + " not found")
        self._pinconfig[pin].update(pinconfig)
        if self._persistent: self.save_to_file()
        return pinconfig

    def get_named_io_pins_config(self):
        namedpins = {}
        for pinconfig in self._pinconfig.values():
            if "name" in pinconfig and pinconfig["name"] is not None:
                namedpins[pinconfig["name"]] = self.get_named_io_pin_config(pinconfig["name"])
        return namedpins;

    def set_named_io_pins_config(self, namedpins):
        for name in namedpins.keys():
            try:
                self.set_named_io_pin_config(name, namedpins[name])
            except KeyError:
                pass
        return self.get_named_io_pins_config()


    def set_io_pins(self, pins):
        if not pins: return
        for pin in pins.keys():
            try:
                self.set_io_pin(pin, pins[pin], persist=False)
            except KeyError:
                pass
        if self._persistent: self.save_to_file()

    def get_named_io_pins(self):
        namedpins = {}
        for pinconfig in self._pinconfig.values():
            if "name" in pinconfig and pinconfig["name"] is not None:
                namedpins[pinconfig["name"]] = self.get_named_io_pin(pinconfig["name"])
        return namedpins;

    def set_named_io_pins(self, namedpins):
        for name in namedpins.keys():
            try:
                self.set_named_io_pin(name, namedpins[name])
            except KeyError:
                pass

    def get_named_io_pin(self, name):
        return self.get_io_pin(self.get_pin_by_name(name))

    def set_named_io_pin(self, name, value):
        pin = self.get_pin_by_name(name)
        if not pin: raise KeyError(name + " not found")
        return self.set_io_pin(pin, value)

    def get_pin_by_name(self, name):
        for pin in self._pinconfig.keys():
            try:
                if self._pinconfig[pin]["name"] == name:
                    return pin
            except KeyError:
                pass
            except TypeError:
                pass
        return None

    def load_from_file(self):
        filename = os.path.join(hombit.HOMEDIR, self.__class__.__name__.lower() + ".json")
        if not os.path.exists(filename):
            return
        try:
            f = open(filename)
            config = self.read_config(json.loads(f.read()))
            self._id = config["id"]
            self._pinconfig = config["pinconfig"]
            self._pinstate = config["pinstate"]
            self._commandstate = config["commandstate"]
        except Exception as e:
            print "Failed to parse configuration: " + str(e)
            print "Continuing without configuration"

    def save_to_file(self):
        filename = os.path.join(hombit.HOMEDIR, self.__class__.__name__.lower() + ".json")
        if not os.path.exists(hombit.HOMEDIR):
            os.makedirs(hombit.HOMEDIR)
        f = open(filename, "w")
        f.write(json.dumps(self.write_config({
            "id": self._id,
            "pinconfig": self._pinconfig,
            "pinstate": self._pinstate,
            "commandstate": self._commandstate,
        })))

    def read_config(self, config):
        return config

    def write_config(self, config):
        return config

    def pin_has_command(self, pin):
        return "commands" in self._pinconfig[pin] and not self._pinconfig[pin]["commands"] is None and len(self._pinconfig[pin]["commands"]) > 0

    def process_commands(self):
        min_interval = 666
        for pin in self._pinconfig.keys():
            pinconfig = self._pinconfig[pin]
            pinstate = {}
            if pin in self._pinstate.keys(): pinstate = self._pinstate[pin]
            if "commands" in pinconfig:
                if pinconfig["commands"] is None:
                    continue
                if "on" in pinstate and not pinstate["on"]:
                    continue
                commands = list(pinconfig["commands"])
                now = time.time()
                for command in commands:
                    if "on" in command and not command["on"]:
                        continue
                    try:
                        name = command["name"]
                        state = {}
                        if str(pin) + "_" + name in self._commandstate:
                            state = self._commandstate[str(pin) + "_" + name]
                        if name == "blink":
                            interval = 3
                            if "interval" in command: interval = float(command["interval"])
                            if interval < min_interval:
                                min_interval = interval
                            interval_off = interval
                            if "intervalOff" in command: interval_off = float(command["intervalOff"])
                            if interval_off < min_interval:
                                min_interval = interval_off
                            lastval = 0
                            lasttime = 0
                            if "lasttime" in state: lasttime = state["lasttime"]
                            if "lastval" in state: lastval = state["lastval"]
                            time_since_last = now - lasttime + 0.099
                            if (lastval and time_since_last >= interval) or (not lastval and time_since_last >= interval_off):
                                print name + " " + str(pin) + " " + str(not lastval)
                                self.set_io_pin(pin, not lastval, hard=True)
                                state["lastval"] = not lastval
                                state["lasttime"] = now
                        else:
                            continue
                        self._commandstate[str(pin) + "_" + name] = state
                    except ValueError as e:
                        print "Command error: ", e
        if min_interval == 666: min_interval = 1
        if min_interval < 0.1: min_interval = 0.1
        self.min_command_interval = min_interval

