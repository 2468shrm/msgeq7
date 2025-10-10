
import digitalio
import analogio
import time

class MSGEQ7:
    """
    Provides support for using an MSI MSGEQ7 seven band graphic equalizer
    IC.
    Product webpage
    https://www.mix-sig.com/index.php/msgeq7-seven-band-graphic-equalizer-display-filter
    Data sheet
    https://www.mix-sig.com/images/datasheets/MSGEQ7.pdf
    """
    # The index into the result list and sample sequence
    BAND_63Hz = 0
    BAND_160Hz = 1
    BAND_400Hz = 2
    BAND_1kHz = 3
    BAND_2_5kHz = 4
    BAND_6_25kHz = 5
    BAND_16kHz = 6

    # Times from the data sheet
    # RESET pulse width (high), min, µs -- 100 ns = 0.1 µs
    TIME_TR_NS = 100

    # RESET to STROBE delay, min, µs -- 72 us
    TIME_TRS_NS = 72000
    
    # STROBE pulse width, min, µs -- 20 µs
    TIME_TS_NS = 20000

    # STROBE to STROBE delay, min, µs -- 72 µs
    TIME_TSS_NS = 72000

    # OUTPUT settling time, min, µs -- 36 µs
    # The time from STROBE fall to initiating analog
    # sample
    TIME_TO_NS = 36000

    def delay(self, delay_ns: int):
        # Record the time on entry
        _now = time.monotonic_ns()
        while time.monotonic_ns() - _now < delay_ns:
            pass

    def __init__(self, pin_strobe:digitalio.DigitalInOut=None,
                 pin_reset:digitalio.DigitalInOut=None,
                 pin_output:analogio.AnalogIn=None) -> None:
        """
        An object for interfacing to a MSGEQ7 IC.
        Args:
            pin_strobe (digitalio.DigitalInOut): The MCU pin connected to
                the STROBE pin of the MSGEQ7
            pin_reset (digitalio.DigitalInOut): The MCU pin connected to
                the RESET pin of the MSGEQ7
            pin_output (analogio.AnalogIn): The MCU pin connected to
                the OUTPUT pin of the MSGEQ7
        """
        # Pin assignments and state construction
        self.pin_strobe = pin_strobe
        self.pin_reset = pin_reset
        self.pin_output= pin_output
        self.channel = [0] * 7

        # The constructor should also reset the MSGEQ7 IC's 
        # output multiplexer sequencer, by asserting and
        # de-asserting the RESET pin. Note the minimum times
        # per the MSGEQ7's datasheet
        self.pin_strobe.value = False
        self.pin_reset.value = False
        self.delay(self.TIME_TR_NS)

        self.pin_reset.value = True
        # Hold/assert time for a min of tr (or more)
        self.delay(self.TIME_TR_NS)
        # deassert (ready to start a new sequence)
        self.reset.value = False

        # Wait trs=72 us (min) before we can assert the first strobe
        self.delay(self.TIME_TRS_NS)

    def sample_sequence(self):
        """
        Generates the needed STROBE and sample sequence to read the
        peak power of each frequency band.
        """

        # Sample each channel in turn                
        for ch in range(0, 7):
            # assert strobe (high)
            self.strobe.value = True
            # Wait ts (or more)
            self.delay(self.TIME_TS_NS)
            # de-assert strobe (low)
            self.strobe.value = False

            # wait to sample and settle, to
            self.delay(self.TIME_TO_NS)
            # read the analog value on the OUT pin and save it
            self.channel[ch] = int (self.pin_output.value)

            # Wait for the next strobe (tss - to = 36 µs, or more)
            self.delay(self.TIME_TSS_NS - self.TIME_TO_NS)
