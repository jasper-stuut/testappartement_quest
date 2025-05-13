from flask import Flask, render_template, send_from_directory, send_file, jsonify
import os
import zipfile
import io
import csv

app = Flask(__name__)
csv_folder = '/home/jstuut/meetsysteem'

def get_latest_error():
    error_file = os.path.join(csv_folder, 'sensorerrors.csv')
    latest_error = {"source": "-", "timestamp": "-", "description": "Geen fouten gevonden."}

    if os.path.exists(error_file):
        with open(error_file, 'r') as f:
            lines = f.readlines()
            if lines:
                last = lines[-1].strip().split(',')
                if len(last) >= 4:
                    latest_error = {
                        "source": last[0],
                        "timestamp": last[1],
                        "description": f"Temp: {last[2]} °C, RH: {last[3]} %"
                    }
    return latest_error

@app.route('/')
def home():
    latest_error = get_latest_error()
    return render_template('index.html', latest_error=latest_error)

@app.route('/latest-error')
def latest_error_api():
    return jsonify(get_latest_error())

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(csv_folder, filename, as_attachment=True)

@app.route('/download/all-csvs.zip')
def download_all_csvs():
    zip_stream = io.BytesIO()
    with zipfile.ZipFile(zip_stream, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for filename in os.listdir(csv_folder):
            if filename.endswith('.csv'):
                filepath = os.path.join(csv_folder, filename)
                zipf.write(filepath, arcname=filename)
    zip_stream.seek(0)
    return send_file(zip_stream, mimetype='application/zip', as_attachment=True, download_name='sensor_data.zip')

@app.route('/graph-data/<filename>')
def graph_data(filename):
    data = {'timestamps': [], 'temperatures': [], 'humidities': []}
    filepath = os.path.join(csv_folder, filename)

    if not os.path.isfile(filepath) or not filename.endswith('.csv'):
        return jsonify({'error': 'Invalid file'}), 400

    with open(filepath) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data['timestamps'].append(row['timestamp'])
            data['temperatures'].append(float(row['temperature_C']))
            data['humidities'].append(float(row['humidity_percent']))

    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

