import time
import array
from carrier_board.m4_feather_can import CarrierBoard
from adafruit_simplemath import map_range
# import board
# import neopixel
from msgeq7 import MSGEQ7

class EqDisplay:
    def __init__(self, num_pixels_per_band: int=0,
                 num_bands: int=0,
                 cb: CarrierBoard=None,
                 msgeq7: MSGEQ7=None) -> None:
        self.num_pixels = num_pixels_per_band
        self.num_bands = num_bands
        self.cb = cb
        self.msgeq7 = msgeq7
        self.last_channel = [0] * 7
    
    def update(self) -> None:
        _x = [map_range(chv, in_min=0, in_max=65535, out_min=0, 
                        out_max=self.num_pixels) for chv in self.msgeq7.channel]
        for ch in num_bands:
            for pi in range(self.num_pixels):
                cb.neopixel[pi] = (0,0,128) if _x[ch] > pi else ((0,0,16) if self.last_channel[ch] > pi else (0,0,0))
        cb.neopixel.show()
        self.last_channel = _x


#
# 
#
carrier_board_config = {
    "init_dio0": { "as_output": True},
    "init_dio1": { "as_output": True},
    "init_ain0": True,
    "init_neopixel": {
        "num_pixels": 7,
    },
}
cb = CarrierBoard(carrier_board_config)

msgeq7 = MSGEQ7(pin_reset=cb.dio0, pin_strobe=cb.dio1, pin_output=cb.ain0)

display = EqDisplay(num_pixels_per_band=7, cb=cb, msgeq7=msgeq7)

# msg.channel[i] is in range of 0-65535
# from simplemath import map_range
# new = map_range(value, in_min=0, in_max=65535, out_min=0, out_max=7)

while True:
    msgeq7.sample_sequence()
    for ch in range(0,7):
        cb.neopixel[ch] = intensity_to_color(msgeq7.channel[ch])
    cb.neopixel.show()
