import os
import uuid
import subprocess
import glob
import json
from flask import Flask, render_template, request, send_from_directory, jsonify
from music21 import converter, midi, instrument

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
AUDIO_FOLDER = 'static/audio'
SOUNDFONT_PATH = '/Users/brandonhebrandonhe/Downloads/FluidR3_GM/FluidR3_GM.sf2'

# Set Tesseract data path for Audiveris
os.environ["TESSDATA_PREFIX"] = os.path.expanduser("~/tessdata")

# Instrument mapping
INSTRUMENT_MAP = {
    "Piano": instrument.Piano(),
    "Violin": instrument.Violin(),
    "Flute": instrument.Flute(),
    "AltoSaxophone": instrument.AltoSaxophone(),
}

# Ensure required folders exist
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, AUDIO_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def update_progress(percentage, message=""):
    with open('progress.json', 'w') as f:
        json.dump({"progress": percentage, "message": message}, f)

@app.route('/', methods=['GET', 'POST'])
def index():
    audio_file = None
    error = None

    if request.method == 'POST':
        update_progress(0, "Starting...")

        for f in glob.glob(os.path.join(OUTPUT_FOLDER, '*')) + glob.glob(os.path.join(AUDIO_FOLDER, '*')):
            os.remove(f)

        file = request.files['file']
        instrument_selected = request.form.get('instrument')

        if file and instrument_selected:
            unique_id = str(uuid.uuid4()).replace('-', '')
            filename = f"{unique_id}_{file.filename}"
            upload_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(upload_path)

            update_progress(10, "Running Audiveris...")
            mxl_paths = run_audiveris(upload_path, unique_id)
            if not mxl_paths:
                update_progress(0, "❌ MusicXML not found. Audiveris may have failed.")
                return render_template('index.html', error="❌ MusicXML not found. Audiveris may have failed.", audio_file=None)

            final_audio_filename = f"{unique_id}.wav"
            audio_output_path = os.path.join(AUDIO_FOLDER, final_audio_filename)
            scores = [converter.parse(path) for path in mxl_paths]

            update_progress(50, "Converting to audio...")
            convert_scores_to_audio(scores, audio_output_path, instrument_selected)

            update_progress(100, "✅ Done!")
            audio_file = final_audio_filename

    return render_template('index.html', audio_file=audio_file, error=error)

@app.route('/progress')
def progress():
    try:
        with open('progress.json', 'r') as f:
            return jsonify(json.load(f))
    except:
        return jsonify({"progress": 0, "message": "Idle"})

def run_audiveris(image_path, uid):
    result = subprocess.run([
        '/Applications/Audiveris.app/Contents/MacOS/audiveris',
        '-batch', image_path,
        '-export',
        '-output', OUTPUT_FOLDER
    ], capture_output=True, text=True)

    print("AUDIVERIS STDOUT:\n", result.stdout)
    print("AUDIVERIS STDERR:\n", result.stderr)

    mxl_files = glob.glob(os.path.join(OUTPUT_FOLDER, '**', '*.mxl'), recursive=True)
    return mxl_files

def convert_scores_to_audio(scores, final_output_path, instrument_name):
    temp_audio_files = []

    for idx, score in enumerate(scores):
        for part in score.parts:
            part.insert(0, INSTRUMENT_MAP.get(instrument_name, instrument.Piano()))

        midi_path = final_output_path.replace('.wav', f'_part{idx}.mid')
        audio_path = final_output_path.replace('.wav', f'_part{idx}.wav')

        try:
            expanded_score = score.expandRepeats()
            print("✅ Successfully expanded repeats")
        except Exception as e:
            print(f"⚠️ Repeat expansion failed: {e}")
            flat = score.flattenUnnecessaryVoices()
            expanded_score = flat.flatten() if flat else score.flatten()

        mf = midi.translate.music21ObjectToMidiFile(expanded_score)
        mf.open(midi_path, 'wb')
        mf.write()
        mf.close()

        subprocess.run([
            'fluidsynth',
            '-ni',
            SOUNDFONT_PATH,
            midi_path,
            '-F',
            audio_path,
            '-r', '44100'
        ])
        temp_audio_files.append(audio_path)

    if len(temp_audio_files) == 1:
        os.rename(temp_audio_files[0], final_output_path)
    else:
        list_file = os.path.join(OUTPUT_FOLDER, 'concat.txt')
        with open(list_file, 'w') as f:
            for file in temp_audio_files:
                f.write(f"file '{os.path.abspath(file)}'\n")
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', list_file, '-c', 'copy', final_output_path
        ])
        for file in temp_audio_files:
            os.remove(file)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(AUDIO_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
