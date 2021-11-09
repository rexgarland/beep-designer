import math
import wave
import struct

SAMPLE_RATE = 44100

def create_beep_data(frequency, amplitude, duration, ramp):
    """
    Creates an array of floating point number represent the audio data of the beep.
    """

    assert frequency > 0 and frequency < SAMPLE_RATE//2, f"Frequency must be above 0 and below {SAMPLE_RATE//2}"
    assert amplitude >= 0 and amplitude <= 1, "Amplitude must be between 0 and 1, inclusive"
    assert ramp*2 < duration, "The ramp is too long. It is applied to both sides and it counted as part of |duration|."

    data = []
    
    num_samples = int(duration * SAMPLE_RATE)
    omega = 2 * math.pi * frequency / SAMPLE_RATE

    ramp_samples = int(ramp * SAMPLE_RATE)
    ramp_omega = math.pi * (1.0 / ramp) / SAMPLE_RATE

    for i in range(ramp_samples):
        ramp_amplitude = amplitude * (0.5 - 0.5 * math.cos( ramp_omega * i ))
        data.append(ramp_amplitude * math.sin( omega * i ))

    for i in range(ramp_samples, num_samples - ramp_samples):
        data.append(amplitude * math.sin( omega * i ))

    for i in range(num_samples - ramp_samples, num_samples):
        j = i - (num_samples - ramp_samples)
        ramp_amplitude = amplitude * (0.5 + 0.5 * math.cos( ramp_omega * j ))
        data.append(ramp_amplitude * math.sin( omega * i ))

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
    ap.add_argument('--amplitude', default=1.0, type=float, help='a float, in the range [0,1]')
    ap.add_argument('--duration', default=0.1, type=float, help='the total duration of the sound, in seconds')
    ap.add_argument('--ramp', default=0.01, type=float, help='the duration of the quarter-cosine ramp, in seconds, applied to boths sides of the sound (c.f. "tukey window")')
    ap.add_argument('--output', default='beep.wav', help='output wav filename')
    args = ap.parse_args()

    data = create_beep_data(args.frequency, args.amplitude, args.duration, args.ramp)
    save(data, args.output)
