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
    Process the request and perform a port scan using nmap based on the scan type selected by the user.
    """
    data = request.json
    scan_type = data.get('scan_type')  # User-selected scan type
    ip = data.get('ip')
    logging.info(f"Received processing request with data: {data}")

    # Generate a unique job_id and directory for this process
    job_id = str(uuid.uuid4())
    unique_dir = str(uuid.uuid4())
    full_output_path = os.path.join(output_directory, unique_dir)
    os.makedirs(full_output_path, exist_ok=True)

    # Define the base command for nmap
    base_command = [
        "nmap",
        "-T4",
        "-n",
        "-Pn",
        "--top-ports", "1000",
        "-oN", os.path.join(full_output_path, "nmap_output.txt"),
        ip
    ]

    # Append the appropriate scan option
    scan_options = {
        "syn_scan": "-sS",
        "tcp_connect_scan": "-sT",
        "udp_scan": "-sU",
        "ack_scan": "-sA",
        "fin_scan": "-sF",
        "xmas_scan": "-sX",
        "null_scan": "-sN",
        "os_detection": "-O",
        "aggressive_scan": "-A",
        "intense_scan": "-T4",
        "custom_nse": "--script=default"
        # Add more scan types as needed
    }

    scan_option = scan_options.get(scan_type)
    if scan_option:
        base_command.insert(1, scan_option)
    else:
        logging.error("Invalid scan type provided")
        return jsonify({"error": "Invalid scan type provided"}), 400

    try:
        subprocess.run(base_command, check=True)
    except Exception as e:
        logging.error(f"Error while executing command: {e}")
        return jsonify({"error": "Failed to process job"}), 500

    try:
        with open(os.path.join(full_output_path, "nmap_output.txt"), 'r') as file:
            scan_results = file.read()
    except Exception as e:
        logging.error(f"Error reading nmap output file: {e}")
        return jsonify({"error": "Failed to read scan results"}), 500

    node3_address = "http://analysis-app:5003/process_scan"
    response = requests.post(node3_address, json={'scan_results': scan_results, 'job_id': job_id})

    if response.status_code == 200:
        response_data = response.json()
        logging.info(f"Sent data to Node 3. Response: {response_data}")
    else:
        logging.error(f"Failed to send data to Node 3. Status: {response.status_code}")

    return jsonify({"message": f"Job processed successfully. Results saved in {full_output_path}", "job_id": job_id}), 200
'''
#method not implemented
@app.route('/download_output/<job_id>', methods=['GET'])
def download_output(job_id):
    try:
        return send_from_directory(directory=os.path.join(output_directory, job_id), filename="nmap_output.txt", as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
'''
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
