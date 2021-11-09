import math
import wave
import struct

SAMPLE_RATE = 44100

class Model:
    def __init__(self, args):
        self.attack = getattr(args, 'attack')
        self.peak = getattr(args, 'peak')
        self.decay = getattr(args, 'decay')
        self.level = getattr(args, 'level')
        self.sustain = getattr(args, 'sustain')
        self.release = getattr(args, 'release')

        assert self.peak >= 0 and self.peak <= 1, "Peak must be between 0 and 1"
        assert self.level <= 0, "Level must be in dB, less than 0"

        self.sustain_amplitude = self.peak * 10**(float(self.level) / 20)

        times = [
            self.attack,
            self.attack+self.decay,
            self.attack+self.decay+self.sustain,
            self.attack+self.decay+self.sustain+self.release
        ]
        self.divisions = [int(time*SAMPLE_RATE) for time in times]

        self.attack_length = self.divisions[0]
        self.decay_length = self.divisions[1] - self.divisions[0]
        self.release_length = self.divisions[3] - self.divisions[2]
        self.num_samples = self.divisions[-1]

    def amplitude_at(self, index):
        if index < self.divisions[0]: # in attack
            return self.peak * (float(index) / self.attack_length)
        elif index < self.divisions[1]: # in decay
            drop = self.peak - self.sustain_amplitude
            since_peak = index-self.divisions[0]
            return self.peak - drop * (float(since_peak) / self.decay_length)
        elif index < self.divisions[2]: # in sustain
            return self.sustain_amplitude
        else: # in release
            to_end = max(self.divisions[3] - index, 0)
            return self.sustain_amplitude * (to_end / self.release_length)


def create_beep_data(frequency, envelope_model):
    """
    Creates an array of floating point number represent the audio data of the beep.
    """

    assert frequency > 0 and frequency < SAMPLE_RATE//2, f"Frequency must be above 0 and below {SAMPLE_RATE//2}"

    data = []
    
    omega = 2 * math.pi * frequency / SAMPLE_RATE

    for i in range(envelope_model.num_samples):
        amplitude = envelope_model.amplitude_at(i)
        data.append(amplitude * math.sin(omega * i))

    return data

def save(data, wavfile):
    with wave.open(wavfile, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.setnframes(len(data))
        f.setcomptype("NONE","no compression")
        for sample in data:
            f.writeframes(struct.pack('h', int(sample * 32767.0)))

if __name__=="__main__":
    import argparse
    ap = argparse.ArgumentParser(description='Create a beep sound')
    ap.add_argument('--frequency', default=440.0, type=float, help=f'frequency in Hz, less than {SAMPLE_RATE//2}')
    ap.add_argument('--attack', default=0.002, type=float, help=f'attack duration, in seconds (float)')
    ap.add_argument('--peak', default=1.0, type=float, help='peak amplitude, in range [0,1] (float)')
    ap.add_argument('--decay', default=0.004, type=float, help='decay duration, in seconds (float)')
    ap.add_argument('--sustain', default=0.04, type=float, help='sustain duration, in seconds (float)')
    ap.add_argument('--level', default=-6, type=float, help='sustain level, in dB (negative float)')
    ap.add_argument('--release', default=0.004, type=float, help='release duration, in seconds (float)')
    ap.add_argument('--output', default='beep.wav', help='output wav filename')
    args = ap.parse_args()

    model = Model(args)
    data = create_beep_data(args.frequency, model)
    save(data, args.output)
