import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import math

class AudioManager:
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self.notes = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
            'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }
        self.set_default_devices()

    def set_default_devices(self):
        devices = sd.query_devices()
        output_devices = [d for d in devices if d['max_output_channels'] > 0]
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        if output_devices:
            default_output = sd.query_devices(kind='output')
            sd.default.device[1] = devices.index(default_output) if default_output else devices.index(output_devices[0])
        if input_devices:
            sd.default.device[0] = devices.index(input_devices[0])

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        sd.default.samplerate = sample_rate

    def set_output_device(self, output_device):
        devices = sd.query_devices()
        device_id = next((i for i, d in enumerate(devices) if d['name'] == output_device), None)
        if device_id is not None:
            try:
                sd.check_output_settings(device=device_id, samplerate=self.sample_rate, channels=2)
                sd.default.device[1] = device_id
            except:
                self.set_default_devices()
        else:
            self.set_default_devices()

    def set_input_device(self, input_device):
        devices = sd.query_devices()
        device_id = next((i for i, d in enumerate(devices) if d['name'] == input_device), None)
        if device_id is not None:
            try:
                sd.check_input_settings(device=device_id, samplerate=self.sample_rate, channels=1)
                sd.default.device[0] = device_id
            except:
                self.set_default_devices()
        else:
            self.set_default_devices()

    def note_to_frequency(self, note, tuning=440.0):
        note_name = note[:-1]
        octave = int(note[-1])
        semitone = self.notes[note_name]
        midi_note = 12 * (octave + 1) + semitone  # Shift up one octave
        # Use high-precision equal temperament formula
        frequency = 2.0 ** ((midi_note - 69) / 12.0) * tuning
        return frequency

    def generate_wave(self, frequency, t, waveform='sine'):
        if waveform == 'triangle':
            # Triangle wave: integral of square wave, scaled to [-1, 1]
            audio = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        elif waveform == 'square':
            # Square wave: sign of sine wave
            audio = np.sign(np.sin(2 * np.pi * frequency * t))
        else:  # Default to sine
            audio = np.sin(2 * np.pi * frequency * t)
        return audio

    def play_sine_wave(self, frequency, duration=2.0, waveform='sine'):
        try:
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            audio = 0.98 * self.generate_wave(frequency, t, waveform)
            # Add octave higher for low notes (below C4, adjusted for octave shift)
            if frequency < self.note_to_frequency("C4"):
                audio += 0.98 * self.generate_wave(frequency * 2, t, waveform)
                audio /= 2
            sd.play(audio.astype(np.float32), self.sample_rate, device=sd.default.device[1])
            sd.wait()
        except:
            pass

    def record_audio(self, duration, output_file):
        try:
            recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, device=sd.default.device[0], dtype='float32')
            sd.wait()
            threshold = 0.01
            non_silent_idx = np.where(np.abs(recording) > threshold)[0]
            if len(non_silent_idx) > 0:
                recording = recording[non_silent_idx[0]:]
            recording = recording / max(np.abs(recording).max(), 1e-10)
            wavfile.write(output_file, self.sample_rate, recording)
        except:
            pass

    def play_sample(self, sample_path):
        try:
            fs, data = scipy.io.wavfile.read(sample_path)
            if data.dtype != np.float32:
                data = data.astype(np.float32) / np.iinfo(data.dtype).max
            sd.play(data, fs, device=sd.default.device[1])
            sd.wait()
        except:
            pass
