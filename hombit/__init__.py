#__all__ = [ "hombit", "simulator" ]

from device import Device
from simulator import Simulator
import api
import os
#from raspberrypi import RaspberryPi

FIRMWARE_VERSION = 1
HOMEDIR = os.path.expanduser("~/.hombit")
