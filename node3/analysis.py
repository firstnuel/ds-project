from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
import openai
import logging
import json
import os
from dotenv import load_dotenv

# This line loads the variables from .env into the environment
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///analysis_results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model definition
class ScanAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(36), unique=True, nullable=False)
    raw_scan_data = db.Column(db.Text, nullable=False)
    ai_analysis = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<ScanAnalysis {self.job_id}>'

# Wrap creation of tables in app context
with app.app_context():
    db.create_all()

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Improved error handling for AI analysis with large data
def get_ai_analysis(raw_scan_data):
    try:
        # Ensure the data size is within a manageable limit
        if len(raw_scan_data) > 10000:
            raw_scan_data = raw_scan_data[:10000]  # Truncate if necessary

        # Define the prompt for the chat-based analysis
        chat_prompt = {
            "model": "gpt-3.5-turbo",  # Specify the chat model you are using
            "messages": [{
                "role": "system",
                "content": "You are a security expert analyzing network scan results."
            }, {
                "role": "user",
                "content": f"Analyze the following network scan results and provide a security analysis:\n{raw_scan_data}"
            }]
        }

        response = openai.ChatCompletion.create(**chat_prompt)
        # Extract the response text from the last message in the chat sequence
        analysis_text = response.choices[0].message['content']
        return analysis_text.strip()
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        raise ValueError(f"Failed to get AI analysis: {str(e)}")

@app.route('/process_scan', methods=['POST'])
def process_scan():
    data = request.json
    job_id = data.get('job_id')
    raw_scan_data = data.get('scan_results')

    if not raw_scan_data or not job_id:
        return jsonify({"error": "Missing data"}), 400

    try:
        analysis_text = get_ai_analysis(raw_scan_data)

        new_entry = ScanAnalysis(job_id=job_id, raw_scan_data=raw_scan_data, ai_analysis=analysis_text)
        db.session.add(new_entry)
        db.session.commit()

        logging.info(f"Data for job_id: {job_id} successfully saved to database.")
        return jsonify({"message": "Analysis saved", "job_id": job_id})
    except Exception as e:
        logging.error(f"Error occurred while adding new entry to the database: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Adjusted streaming response for correctness and safety
@app.route('/get_combined_results/<job_id>', methods=['GET'])
def get_combined_results(job_id):
    """
    Retrieves the combined results of a scan, including both the raw scan data
    and the AI-generated analysis, for a given job_id.

    Parameters:
    - job_id (str): The unique identifier for the scan job.

    Returns:
    - Flask Response: A JSON object containing the job_id, raw_scan_data,
      and ai_analysis. Returns a 404 error if no results are found for the job_id.
    """
    result = ScanAnalysis.query.filter_by(job_id=job_id).first()
    if result:
        # Properly escape and serialize JSON data
        response_data = json.dumps({
            "job_id": job_id,
            "raw_scan_data": result.raw_scan_data,
            "ai_analysis": result.ai_analysis
        })
        return Response(response_data, mimetype='application/json')
    else:
        return jsonify({"error": "Results not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True,)
