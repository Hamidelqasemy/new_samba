from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from processing.file_processor import process_files
from agents import analyze_proposals
import os
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    try:
        print("Request received")
        if 'files' not in request.files:
            print("No files in request")
            return jsonify({"error": "No files uploaded"}), 400
            
        files = request.files.getlist('files')
        print(f"Received {len(files)} files")
        
        if len(files) < 1:  # Allow single file uploads
            print("No valid files uploaded")
            return jsonify({"error": "Please upload at least 1 file"}), 400

        proposals = process_files(files)
        print("Processed files:", [p['filename'] for p in proposals])
        
        analysis = analyze_proposals(proposals)
        print("Analysis completed")
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)