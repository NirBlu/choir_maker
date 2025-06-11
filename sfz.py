import os

class SFZGenerator:
    def __init__(self):
        self.note_to_midi = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
            'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }

    def note_to_midi_number(self, note):
        note_name = note[:-1]
        octave = int(note[-1])
        return 12 * octave + self.note_to_midi[note_name]

    def generate_sfz(self, samples, output_file, sample_dir, sfz_params=None):
        sfz_params = sfz_params or {
            'ampeg_attack': 0.000,
            'ampeg_release': 0.01,
            'ampeg_sustain': 100,
            'amp_veltrack': 100,
            'loop_mode': 'no_loop',
            'loop_start': 0,
            'loop_end': 0
        }
        sfz_content = "<group>\n"
        sfz_content += f" ampeg_attack={sfz_params['ampeg_attack']:.3f}\n"
        sfz_content += f" ampeg_release={sfz_params['ampeg_release']:.3f}\n"
        sfz_content += f" ampeg_sustain={sfz_params['ampeg_sustain']:.1f}\n"
        sfz_content += f" amp_veltrack={sfz_params['amp_veltrack']:.1f}\n"
        sfz_content += f" loop_mode={sfz_params['loop_mode']}\n"
        if sfz_params['loop_mode'] in ['loop_continuous', 'loop_sustain']:
            sfz_content += f" loop_start={sfz_params['loop_start']}\n"
            sfz_content += f" loop_end={sfz_params['loop_end']}\n"
        sfz_content += "\n"
        pan_values = [-30, -15, 15, 30]
        for note, sample_list in samples.items():
            midi_note = self.note_to_midi_number(note)
            for i, sample_path in enumerate(sample_list):
                sample_name = os.path.basename(sample_path)
                pan = pan_values[i % len(pan_values)]
                sfz_content += f"<region> sample={sample_name} key={midi_note} pan={pan}\n"
            sfz_content += "\n"

        with open(output_file, 'w') as f:
            f.write(sfz_content)
