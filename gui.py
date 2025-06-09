import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import os

class ChoirRecorderGUI:
    def __init__(self, root, start_callback, recording_complete_callback, app):
        self.root = root
        self.start_callback = start_callback
        self.recording_complete_callback = recording_complete_callback
        self.app = app
        self.root.title("Choir Sample Recorder")
        self.root.geometry("400x700")
        self.monitoring = False
        self.tuning = 440.0
        self.waveform = 'triangle'  # Default to triangle wave
        self.setup_initial_screen()

    def setup_initial_screen(self):
        self.clear_frame()
        tk.Label(self.root, text="Tuning (Hz):").pack(pady=5)
        self.tuning_entry = tk.Entry(self.root)
        self.tuning_entry.insert(0, "440")
        self.tuning_entry.pack(pady=5)

        tk.Label(self.root, text="Sample Length (seconds):").pack(pady=5)
        self.sample_length_entry = tk.Entry(self.root)
        self.sample_length_entry.insert(0, "2.5")
        self.sample_length_entry.pack(pady=5)

        tk.Label(self.root, text="Countdown Length (seconds):").pack(pady=5)
        self.countdown_entry = tk.Entry(self.root)
        self.countdown_entry.insert(0, "3")
        self.countdown_entry.pack(pady=5)

        tk.Label(self.root, text="Start Note:").pack(pady=5)
        self.notes = []
        for octave in range(2, 5):
            for note in ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']:
                self.notes.append(f"{note}{octave}")
        self.notes.append('C5')
        self.start_note_var = tk.StringVar(self.root)
        self.start_note_var.set("C2")
        self.start_note_menu = tk.OptionMenu(self.root, self.start_note_var, *self.notes)
        self.start_note_menu.pack(pady=5)

        tk.Label(self.root, text="Waveform:").pack(pady=5)
        self.waveform_var = tk.StringVar(self.root)
        self.waveform_var.set("triangle")
        self.waveform_menu = tk.OptionMenu(self.root, self.waveform_var, "sine", "triangle", "square")
        self.waveform_menu.pack(pady=5)

        tk.Label(self.root, text="Microphone Input:").pack(pady=5)
        self.input_devices = [d['name'] for d in sd.query_devices() if d['max_input_channels'] > 0]
        self.input_var = tk.StringVar(self.root)
        if self.input_devices:
            self.input_var.set(self.input_devices[0])
        self.input_menu = tk.OptionMenu(self.root, self.input_var, *self.input_devices, command=self.update_sample_rates)
        self.input_menu.pack(pady=5)

        tk.Label(self.root, text="Output Device:").pack(pady=5)
        self.output_devices = [d['name'] for d in sd.query_devices() if d['max_output_channels'] > 0]
        self.output_var = tk.StringVar(self.root)
        default_output = sd.query_devices(kind='output')['name'] if sd.query_devices(kind='output') else self.output_devices[0] if self.output_devices else ""
        self.output_var.set(default_output)
        self.output_menu = tk.OptionMenu(self.root, self.output_var, *self.output_devices)
        self.output_menu.pack(pady=5)

        tk.Label(self.root, text="Sample Rate (Hz):").pack(pady=5)
        self.sample_rate_var = tk.StringVar(self.root)
        self.sample_rate_menu = tk.OptionMenu(self.root, self.sample_rate_var, "")
        self.sample_rate_menu.pack(pady=5)
        self.update_sample_rates()

        self.volume_canvas = tk.Canvas(self.root, width=200, height=20, bg='white')
        self.volume_canvas.pack(pady=5)
        self.volume_bar = self.volume_canvas.create_rectangle(0, 0, 0, 20, fill='green')

        tk.Button(self.root, text="Test Input", command=self.test_input).pack(pady=5)
        tk.Button(self.root, text="Test Output", command=self.test_output).pack(pady=5)
        tk.Button(self.root, text="Start", command=self.start_recording, font=("Arial", 16)).pack(pady=20)
        self.start_volume_monitor()

    def test_input(self):
        try:
            self.monitoring = True
            device_name = self.input_var.get()
            device_id = next((i for i, d in enumerate(sd.query_devices()) if d['name'] == device_name), None)
            if device_id is not None:
                sd.default.device[0] = device_id
            sample_rate = int(self.sample_rate_var.get())
            self.update_volume_meter(sample_rate)
            self.root.after(5000, lambda: setattr(self, 'monitoring', False))
        except:
            self.monitoring = False

    def test_output(self):
        try:
            output_device = self.output_var.get()
            device_id = next((i for i, d in enumerate(sd.query_devices()) if d['name'] == output_device), None)
            sample_rate = int(self.sample_rate_var.get())
            t = np.linspace(0, 1, int(sample_rate), False)
            audio = 0.5 * np.sin(2 * np.pi * 440 * t)
            sd.play(audio.astype(np.float32), sample_rate, device=device_id)
            sd.wait()
        except:
            pass

    def update_sample_rates(self, *args):
        try:
            device_name = self.input_var.get()
            output_name = self.output_var.get()
            input_id = next((i for i, d in enumerate(sd.query_devices()) if d['name'] == device_name), None)
            output_id = next((i for i, d in enumerate(sd.query_devices()) if d['name'] == output_name), None)
            self.sample_rates = [44100, 48000, 96000]
            supported_rates = set()
            test_rates = [8000, 16000, 22050, 44100, 48000, 96000, 192000]
            if input_id is not None:
                for rate in test_rates:
                    try:
                        sd.check_input_settings(device=input_id, samplerate=rate, channels=1)
                        supported_rates.add(rate)
                    except:
                        pass
            if output_id is not None:
                for rate in test_rates:
                    try:
                        sd.check_output_settings(device=output_id, samplerate=rate, channels=2)
                        supported_rates.add(rate)
                    except:
                        pass
            if supported_rates:
                self.sample_rates = sorted(supported_rates)
            self.sample_rate_var.set(str(self.sample_rates[0] if 48000 not in self.sample_rates else 48000))
            menu = self.sample_rate_menu["menu"]
            menu.delete(0, "end")
            for rate in self.sample_rates:
                menu.add_command(label=str(rate), command=lambda r=rate: self.sample_rate_var.set(str(r)))
        except:
            pass

    def start_volume_monitor(self, *args):
        self.monitoring = True
        try:
            device_name = self.input_var.get()
            device_id = next((i for i, d in enumerate(sd.query_devices()) if d['name'] == device_name), None)
            if device_id is not None:
                sd.default.device[0] = device_id
            sample_rate = int(self.sample_rate_var.get())
            self.update_volume_meter(sample_rate)
        except:
            self.monitoring = False

    def update_volume_meter(self, sample_rate):
        if not self.monitoring:
            return
        try:
            recording = sd.rec(1024, samplerate=sample_rate, channels=1, blocking=False, dtype='float32')
            sd.wait()
            amplitude = np.abs(recording).max()
            width = min(200, int(amplitude * 400))
            self.volume_canvas.coords(self.volume_bar, 0, 0, width, 20)
            self.root.update_idletasks()
        except:
            self.monitoring = False
            return
        self.root.after(50, self.update_volume_meter, sample_rate)

    def start_recording(self):
        self.monitoring = False
        try:
            self.tuning = float(self.tuning_entry.get())
            sample_length = float(self.sample_length_entry.get())
            countdown_length = int(self.countdown_entry.get())
            sample_rate = int(self.sample_rate_var.get())
            output_device = self.output_var.get()
            input_device = self.input_var.get()
            start_note = self.start_note_var.get()
            self.waveform = self.waveform_var.get()
            if self.tuning <= 0 or sample_length <= 0 or sample_rate <= 0 or countdown_length < 1:
                raise ValueError
            self.start_callback(self.tuning, sample_length, sample_rate, output_device, input_device, start_note, countdown_length)
        except:
            pass

    def show_countdown(self, note, callback, countdown_length):
        self.clear_frame()
        self.countdown_label = tk.Label(self.root, text=f"Get ready for {note}...", font=("Arial", 20))
        self.countdown_label.pack(pady=50)
        self.root.update_idletasks()
        self.root.after(1000, lambda: self.countdown_step(note, countdown_length, callback))

    def countdown_step(self, note, count, callback):
        if count > 0:
            self.countdown_label.config(text=f"{count}...")
            self.root.update_idletasks()
            self.root.after(1000, lambda: self.countdown_step(note, count - 1, callback))
        else:
            self.countdown_label.config(text="Recording!")
            self.root.update_idletasks()
            self.root.after(500, callback)

    def show_recording_options(self, note):
        self.clear_frame()
        tk.Label(self.root, text=f"Recorded {note}", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Play Back", command=lambda: self.play_sample(note)).pack(pady=5)
        tk.Button(self.root, text="Play Note", command=lambda: self.play_note(note)).pack(pady=5)
        tk.Button(self.root, text="Keep and Proceed", command=lambda: self.recording_complete_callback("keep", note)).pack(pady=5)
        tk.Button(self.root, text="Keep and Record Again", command=lambda: self.recording_complete_callback("keep_again", note)).pack(pady=5)
        tk.Button(self.root, text="Discard and Retry", command=lambda: self.recording_complete_callback("discard", note)).pack(pady=5)
        tk.Button(self.root, text="Skip", command=lambda: self.recording_complete_callback("skip", note)).pack(pady=5)
        tk.Button(self.root, text="Finish", command=lambda: self.confirm_finish()).pack(pady=5)
        self.root.update_idletasks()

    def confirm_finish(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to finish and generate the SFZ file?"):
            self.show_sfz_settings()

    def show_sfz_settings(self):
        self.clear_frame()
        tk.Label(self.root, text="SFZ Settings", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="SFZ Filename:").pack(pady=5)
        self.filename_entry = tk.Entry(self.root)
        self.filename_entry.insert(0, "choir")
        self.filename_entry.pack(pady=5)

        tk.Label(self.root, text="Attack Time (seconds):").pack(pady=5)
        self.attack_entry = tk.Entry(self.root)
        self.attack_entry.insert(0, "0.000")
        self.attack_entry.pack(pady=5)

        tk.Label(self.root, text="Release Time (seconds):").pack(pady=5)
        self.release_entry = tk.Entry(self.root)
        self.release_entry.insert(0, "0.01")
        self.release_entry.pack(pady=5)

        tk.Label(self.root, text="Sustain Level (%):").pack(pady=5)
        self.sustain_entry = tk.Entry(self.root)
        self.sustain_entry.insert(0, "100")
        self.sustain_entry.pack(pady=5)

        tk.Label(self.root, text="Amp Velocity Track (%):").pack(pady=5)
        self.amp_veltrack_entry = tk.Entry(self.root)
        self.amp_veltrack_entry.insert(0, "100")
        self.amp_veltrack_entry.pack(pady=5)

        tk.Label(self.root, text="Loop Mode:").pack(pady=5)
        self.loop_mode_var = tk.StringVar(self.root)
        self.loop_mode_var.set("no_loop")
        self.loop_mode_menu = tk.OptionMenu(self.root, self.loop_mode_var, "no_loop", "one_shot", "loop_continuous", "loop_sustain")
        self.loop_mode_menu.pack(pady=5)

        tk.Label(self.root, text="Loop Start (samples):").pack(pady=5)
        self.loop_start_entry = tk.Entry(self.root)
        self.loop_start_entry.insert(0, "0")
        self.loop_start_entry.pack(pady=5)

        tk.Label(self.root, text="Loop End (samples):").pack(pady=5)
        self.loop_end_entry = tk.Entry(self.root)
        self.loop_end_entry.insert(0, "0")
        self.loop_end_entry.pack(pady=5)

        tk.Button(self.root, text="Generate SFZ", command=self.generate_sfz).pack(pady=20)
        self.root.update_idletasks()

    def generate_sfz(self):
        try:
            filename = self.filename_entry.get().strip()
            if not filename.endswith('.sfz'):
                filename += '.sfz'
            sfz_params = {
                'ampeg_attack': float(self.attack_entry.get()),
                'ampeg_release': float(self.release_entry.get()),
                'ampeg_sustain': float(self.sustain_entry.get()),
                'amp_veltrack': float(self.amp_veltrack_entry.get()),
                'loop_mode': self.loop_mode_var.get(),
                'loop_start': int(self.loop_start_entry.get()),
                'loop_end': int(self.loop_end_entry.get()),
                'filename': filename
            }
            self.recording_complete_callback("finish", None, sfz_params)
        except:
            messagebox.showerror("Error", "Invalid SFZ parameters or filename. Please enter valid values.")
            self.show_sfz_settings()

    def play_sample(self, note):
        sample_path = os.path.join("choir_samples", f"{note}_{len(self.app.recorded_samples.get(note, [])) + 1}.wav")
        if os.path.exists(sample_path):
            try:
                fs, data = scipy.io.wavfile.read(sample_path)
                if data.dtype != np.float32:
                    data = data.astype(np.float32) / np.iinfo(data.dtype).max
                output_device = self.output_var.get()
                device_id = next((i for i, d in enumerate(sd.query_devices()) if d['name'] == output_device), None)
                sd.play(data, fs, device=device_id)
                sd.wait()
            except:
                pass

    def play_note(self, note):
        try:
            output_device = self.output_var.get()
            device_id = next((i for i, d in enumerate(sd.query_devices()) if d['name'] == output_device), None)
            sample_rate = int(self.sample_rate_var.get())
            t = np.linspace(0, 2.0, int(sample_rate * 2.0), False)
            frequency = self.app.audio_manager.note_to_frequency(note, self.tuning)
            audio = 0.98 * self.app.audio_manager.generate_wave(frequency, t, self.waveform)
            if frequency < self.app.audio_manager.note_to_frequency("C4", self.tuning):
                audio += 0.98 * self.app.audio_manager.generate_wave(frequency * 2, t, self.waveform)
                audio /= 2
            sd.play(audio.astype(np.float32), sample_rate, device=device_id)
            sd.wait()
        except Exception as e:
            print(f"Failed to play note: {str(e)}")

    def show_completion(self, compile_callback):
        self.clear_frame()
        tk.Label(self.root, text="Recording Complete!", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Generate SFZ", command=compile_callback).pack(pady=20)
        self.root.update_idletasks()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.update_idletasks()
