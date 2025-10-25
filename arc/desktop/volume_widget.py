import pyaudio, struct, math
from arc.core import Slider, config

class AudioLevelSlider(Slider):
    def __init__(self, rect, rate=44100, chunk=1024):
        # we don’t need a callback or dragging, so just init value=0
        super().__init__(rect, 0, 100, 0, callback=None)
        self.dragging = False                # disable user drag
        self.rate    = rate
        self.chunk   = chunk
        # open mic input
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

    def handle_event(self, event):
        # override to ignore mouse events
        pass

    def update(self):
        # read a block of audio, compute normalized RMS
        data = self.stream.read(self.chunk, exception_on_overflow=False)
        count = len(data)//2
        samples = struct.unpack(f"{count}h", data)
        sum_squares = sum(s*s for s in samples)
        rms = math.sqrt(sum_squares/count) / 32768.0
        # map to 0–100
        self.value = max(0, min(100, rms * 100))
        self._update_knob_x()    # reposition the knob

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
