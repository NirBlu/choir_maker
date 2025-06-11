Choir Maker
Choir Maker is a Python application that simplifies the creation of SFZ files, primarily for vocal sample libraries, but flexible enough for other instruments or sound types. It helps musicians and sound designers organize audio samples and generate SFZ files for use in digital audio workstations (DAWs) and samplers.
Features

Creates SFZ files from user-provided audio samples.
Supports customizable key ranges, velocity layers, and sample mappings.
Optimized for vocal libraries (e.g., choirs, soloists) but adaptable for any sampled sound.
Command-line interface for straightforward configuration.

Use Cases

Building vocal sample libraries for virtual choirs or solo vocalists.
Creating SFZ instruments for other sounds like strings, percussion, or experimental audio.
Streamlining workflows for virtual instrument design.

Video Tutorial: https://youtu.be/FA-fBZdOyyw?si=pRb5DQvSkC1tis9l

Installation

Clone the repository:git clone https://github.com/nirblu/choir_maker.git
cd choir-maker


Install dependencies:pip install -r requirements.txt



Usage
Run the script and follow the prompts to specify your sample files and mapping settings:
python choir_maker.py

Example
To create an SFZ file for a vocal library:

Organize your audio samples (e.g., WAV files) in a folder.
Run the app and input the folder path, key ranges, and velocity settings.
The app generates an SFZ file ready for use in samplers.

Contributing
Contributions are welcome! Please submit issues or pull requests to add features, fix bugs, or improve documentation.
License
MIT License
