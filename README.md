# 🎼 Treble — Sheet Music to Audio Converter

Treble is a local web app that converts sheet music images into playable audio. Upload a photo or scan of sheet music, choose an instrument, and get a WAV file back.

---

## How It Works

1. You upload a sheet music image (PNG, JPG, or PDF)
2. [Audiveris](https://github.com/Audiveris/audiveris) performs optical music recognition (OMR) and converts it to MusicXML
3. [music21](https://web.mit.edu/music21/) parses the MusicXML and generates a MIDI file
4. [FluidSynth](https://www.fluidsynth.org/) renders the MIDI to a WAV audio file using a soundfont
5. The audio is served back to you in the browser for playback and download

---

## Requirements

Make sure the following are installed before running Treble:

- Python 3.11+
- [Audiveris](https://github.com/Audiveris/audiveris/releases) (installed at `/Applications/Audiveris.app`)
- [FluidSynth](https://www.fluidsynth.org/) — `brew install fluid-synth`
- [FFmpeg](https://ffmpeg.org/) — `brew install ffmpeg`
- [Tesseract](https://github.com/tesseract-ocr/tesseract) + tessdata — required by Audiveris
- A SoundFont `.sf2` file (see setup below)

---

## Installation

**1. Clone or download this project:**
```bash
cd ~/your-project-folder
```

**2. Install Python dependencies:**
```bash
pip install flask music21
```

**3. Install system dependencies (macOS):**
```bash
brew install fluid-synth ffmpeg tesseract
```

**4. Set up tessdata for Audiveris:**
```bash
mkdir -p ~/tessdata
# Download eng.traineddata from https://github.com/tesseract-ocr/tessdata
# and place it in ~/tessdata/
```

**5. Locate your SoundFont:**
```bash
find /opt/homebrew /usr/local -name "*.sf2" 2>/dev/null
```

Update `SOUNDFONT_PATH` in `treble.py` to match the path found.

---

## Project Structure

```
your-project/
├── treble.py               # Main Flask app
├── templates/
│   └── index.html          # Web UI
├── static/
│   └── audio/              # Generated WAV files served here
├── uploads/                # Temporary uploaded sheet music files
├── output/                 # Audiveris MusicXML output
└── progress.json           # Tracks conversion progress for the UI
```

---

## Running the App

```bash
/Users/your-username/.pyenv/versions/3.11.9/bin/python treble.py
```

Then open your browser to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Configuration

At the top of `treble.py`, update these variables as needed:

| Variable | Description |
|---|---|
| `SOUNDFONT_PATH` | Path to your `.sf2` soundfont file |
| `UPLOAD_FOLDER` | Where uploaded images are saved |
| `OUTPUT_FOLDER` | Where Audiveris writes MusicXML |
| `AUDIO_FOLDER` | Where generated WAV files are saved |

---

## Supported Instruments

- Piano
- Violin
- Flute
- Alto Saxophone

To add more instruments, update the `INSTRUMENT_MAP` dictionary in `treble.py` using any instrument from the [music21 instrument module](https://web.mit.edu/music21/doc/moduleReference/moduleInstrument.html).

---

## Troubleshooting

**No audio plays after conversion**
- Check that `SOUNDFONT_PATH` points to a valid `.sf2` file
- Run fluidsynth manually to test: `fluidsynth -ni -F test.wav -r 44100 /path/to/font.sf2 /path/to/file.mid`
- Check the terminal for `FLUIDSYNTH STDERR` output after a conversion

**Audiveris fails / no MusicXML found**
- Make sure Audiveris is installed at `/Applications/Audiveris.app`
- Check that `~/tessdata/eng.traineddata` exists
- Try running Audiveris manually on your image to see its output

**ModuleNotFoundError: No module named 'flask'**
- Install into the correct Python: `/path/to/python3.11 -m pip install flask music21`

---

## License

MIT — free to use and modify.
