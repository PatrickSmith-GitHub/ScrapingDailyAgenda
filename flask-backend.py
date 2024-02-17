from flask import Flask, render_template, request, jsonify
import requests
from threading import Event
import subprocess
import time

app = Flask(__name__)

logs_received_event = Event()
title_textblock_map = None

# Define route for serving index.html
@app.route('/')          
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

# Route for handling scraping request
@app.route('/scrape', methods=['POST'])
def scrape():
    # Get selected school from request data
    data = request.json
    school = data['school']


    initiate_scraping(school)

    return jsonify({"message": "Scraping request accepted."}), 200

def initiate_scraping(school):
    python_file_path = f'/app/Scraping-Scripts/{school}scraping.py'
    # Receive the log data from the scraping container
    subprocess.run(['python', python_file_path])

def finish_scraping(title_textblock_map):
    data_to_send = {'logs': title_textblock_map}  
    # Send the data as a JSON response to the JavaScript file
    return jsonify(data_to_send)

@app.route('/receive-logs', methods=['GET', 'POST'])
def receive_logs():
    global title_textblock_map
    if request.method == 'POST':
        try:
            # Receive logs data from request body
            title_textblock_map = request.json
            # Set event to indicate logs are received
            logs_received_event.set()
            return 'Logs received successfully.', 200
        except Exception as e:
            print(f"Error: {e}")
            return 'Error receiving logs.', 500
    elif request.method == 'GET':
        # Wait for logs if they haven't been received yet
        if not logs_received_event.is_set():
            logs_received_event.wait()
        logs_data = title_textblock_map
        time.sleep(1)
        print(logs_data)
        return jsonify(logs_data), 200

if __name__ == '__main__':
    app.run(debug=True)