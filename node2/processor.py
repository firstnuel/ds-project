from flask import Flask, request, jsonify, send_from_directory
import subprocess
import uuid
import os
import logging
import requests

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Change this path to a directory inside the Docker container
output_directory = "/app/output"

@app.route('/process', methods=['POST'])
def process():
    """
    Process the request and perform a port scan using nmap.

    Returns:
        A JSON response containing the job ID and the path where the results are saved.
    """
    data = request.json
    logging.info(f"Received processing request with data: {data}")

    # Generate a unique job_id and directory for this process
    job_id = str(uuid.uuid4())
    ip = data.get('ip')
    unique_dir = str(uuid.uuid4())
    full_output_path = os.path.join(output_directory, unique_dir)
    os.makedirs(full_output_path, exist_ok=True)  # Create the directory

    try:
        subprocess.run([
            "nmap",
            "-T4",  # Use a faster timing template that's less aggressive than T5
            "-n",   # Skip DNS resolution to save time
            "-Pn",  # Skip ping scan, assuming all hosts are up. Useful for hosts that block ping.
            "--top-ports", "1000",  # Scan the top 1000 most common ports instead of all 65535
            "-oN", os.path.join(full_output_path, "nmap_output.txt"),  # Save the output to a file
            ip  # Target IP address or hostname
        ], check=True)

    except Exception as e:
        logging.error(f"Error while executing command: {e}")
        return jsonify({"error": "Failed to process job"}), 500


    # Read the nmap output file and prepare data
    try:
        with open(os.path.join(full_output_path, "nmap_output.txt"), 'r') as file:
            scan_results = file.read()
    except Exception as e:
        logging.error(f"Error reading nmap output file: {e}")
        return jsonify({"error": "Failed to read scan results"}), 500

    # Prepare and send data to Node 3, including the scan results
    node3_address = "http://analysis-app:5003/process_scan"  # Ensure this is the correct endpoint
    response = requests.post(node3_address, json={'scan_results': scan_results, 'job_id': job_id})

    if response.status_code == 200:
        # Safe to parse JSON and log
        response_data = response.json()
        logging.info(f"Sent data to Node 3. Response status: {response.status_code}, Response data: {response_data}")
    else:
        # Log without parsing JSON to avoid errors
        logging.error(f"Failed to send data to Node 3. Response status: {response.status_code}")

    return jsonify({"message": f"Job processed successfully. Results saved in {full_output_path}", "job_id": job_id}), 200

@app.route('/download_output/<job_id>', methods=['GET'])
def download_output(job_id):
    file_path = os.path.join(output_directory, job_id, "nmap_output.txt")
    
    try:
        return send_from_directory(directory=os.path.join(output_directory, job_id), filename="nmap_output.txt", as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True,)

