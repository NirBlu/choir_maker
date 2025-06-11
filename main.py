import tkinter as tk
from gui import ChoirRecorderGUI
from audio import AudioManager
from sfz import SFZGenerator
import os
import platform
import subprocess

class ChoirRecorderApp:
    def __init__(self):
        self.root = tk.Tk()
        self.audio_manager = AudioManager()
        self.sfz_generator = SFZGenerator()
        self.output_dir = "choir_samples"
        os.makedirs(self.output_dir, exist_ok=True)
        self.gui = ChoirRecorderGUI(self.root, self.start_recording, self.on_recording_complete, self)
        self.current_note = None
        self.notes = self.generate_note_sequence()
        self.recorded_samples = {}
        self.countdown_length = 3

    def generate_note_sequence(self):
        notes = []
        octave = 2
        while True:
            for note in ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']:
                notes.append(f"{note}{octave}")
            octave += 1
            if octave > 10:
                break
        return notes

    def start_recording(self, tuning, sample_length, sample_rate, output_device, input_device, start_note, countdown_length):
        try:
            self.tuning = float(tuning)
            self.sample_length = float(sample_length)
            self.countdown_length = countdown_length
            self.audio_manager.set_sample_rate(sample_rate)
            self.audio_manager.set_output_device(output_device)
            self.audio_manager.set_input_device(input_device)
            self.current_note_idx = self.notes.index(start_note) if start_note in self.notes else 0
            self.process_next_note()
        except:
            pass

    def process_next_note(self):
        if self.current_note_idx < len(self.notes):
            self.current_note = self.notes[self.current_note_idx]
            self.play_note_guide()
        else:
            self.gui.show_completion(self.compile_sfz)

    def play_note_guide(self):
        try:
            note_freq = self.audio_manager.note_to_frequency(self.current_note, self.tuning)
            self.audio_manager.play_sine_wave(note_freq)
            self.gui.show_countdown(self.current_note, self.start_note_recording, self.countdown_length)
        except:
            self.gui.show_countdown(self.current_note, self.start_note_recording, self.countdown_length)

    def start_note_recording(self):
        try:
            output_file = os.path.join(self.output_dir, f"{self.current_note}_{len(self.recorded_samples.get(self.current_note, [])) + 1}.wav")
            self.audio_manager.record_audio(self.sample_length, output_file)
            self.gui.show_recording_options(self.current_note)
        except:
            self.gui.show_recording_options(self.current_note)

    def on_recording_complete(self, action, note, sfz_params=None):
        try:
            if action == "keep":
                if note not in self.recorded_samples:
                    self.recorded_samples[note] = []
                self.recorded_samples[note].append(os.path.join(self.output_dir, f"{note}_{len(self.recorded_samples[note]) + 1}.wav"))
                self.current_note_idx += 1
                self.process_next_note()
            elif action == "keep_again":
                if note not in self.recorded_samples:
                    self.recorded_samples[note] = []
                self.recorded_samples[note].append(os.path.join(self.output_dir, f"{note}_{len(self.recorded_samples[note]) + 1}.wav"))
                self.play_note_guide()
            elif action == "discard":
                try:
                    os.remove(os.path.join(self.output_dir, f"{note}_{len(self.recorded_samples.get(note, [])) + 1}.wav"))
                except FileNotFoundError:
                    pass
                self.play_note_guide()
            elif action == "skip":
                self.current_note_idx += 1
                self.process_next_note()
            elif action == "finish":
                self.compile_sfz(sfz_params)
        except:
            pass

    def compile_sfz(self, sfz_params=None):
        try:
            output_sfz = os.path.join(self.output_dir, sfz_params.get('filename', 'choir.sfz') if sfz_params else 'choir.sfz')
            self.sfz_generator.generate_sfz(self.recorded_samples, output_sfz, self.output_dir, sfz_params)
            self.open_output_folder()
            self.root.destroy()
        except:
            pass

    def open_output_folder(self):
        folder_path = os.path.abspath(self.output_dir)
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
        except:
            pass

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ChoirRecorderApp()
    app.run()
