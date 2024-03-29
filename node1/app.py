import requests
from flask import Flask, render_template, request, jsonify
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    ip = request.form['ip']
    scan_type = request.form['scan_type']  # Retrieve the scan type selected by the user
    # Send the job to Node 2
    node2_address = 'http://processor-app:5002/process'
    job_data = {"ip": ip, "scan_type": scan_type}  # Include scan type in the job data
    logging.info(f"Sending scan job to Node 2 with data {job_data}")
    response = requests.post(node2_address, json=job_data)

    if response.status_code == 200:
        # Assuming Node 2 returns a job_id
        job_id = response.json().get('job_id')
        # Fetch combined results from Node 3
        node3_address = f'http://analysis-app:5003/get_combined_results/{job_id}'
        analysis_response = requests.get(node3_address)
        if analysis_response.status_code == 200:
            # Directly render a template with the results, including the IP address and scan type
            results = analysis_response.json()
            return render_template('results.html', results=results, ip_address=ip, scan_type=scan_type)
        else:
            logging.error("Failed to fetch analysis results")
            return "Failed to fetch analysis results", 500
    else:
        logging.error("Failed to submit scan job")
        return "Failed to submit scan job", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
