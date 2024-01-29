from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import socket
import json
from datetime import datetime
import threading
import os
import time
from pathlib import Path

app = Flask(__name__)

web_port = 3000
socket_port = 5000
UDP_IP = '127.0.0.1'
messages = {}

@app.route('/')
def index():
    file = 'index.html'
    return render_template(file)

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html'), 404


def run_socket_server(UDP_IP, socket_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (UDP_IP, socket_port)
    sock.bind(server_address)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            print(f'Отримано повідомлення: {data.decode()} від: {address}')
            sock.sendto(data, address)
            print(f'Надіслано повідомлення: {data.decode()} за адресою: {address}')
            decoded_data = json.loads(data.decode('utf-8'))
            save_to_json(decoded_data)

    except KeyboardInterrupt:
        print(f'Stopping the server')
    finally:
        sock.close()


@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message_text = request.form['message']

        data = {
            'timestamp': str(datetime.now()),
            'username': username,
            'message': message_text
        }

        send_to_socket(data)
        return render_template('message.html', data=data)

    return render_template('message.html')

def send_to_socket(data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        server_address = (UDP_IP, socket_port)
        s.sendto(json.dumps(data).encode('utf-8'), server_address)
        
def add_message(username, message):
    timestamp = str(datetime.now())
    messages[timestamp] = {"username": username, "message": message}
    return messages

def save_to_json(data):
    add_message(data['username'], data['message'])

    with open('storage/data.json', 'w') as json_file:
        json.dump(messages, json_file, indent=2)   
        
def save_to_json(data):
    add_message(data['username'], data['message'])
    current_directory = Path(__file__).resolve().parent
    file_path = current_directory / 'storage' / 'data.json'
    
    try:
        with open(file_path, 'r') as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        existing_data = {}
    
    existing_data.update(messages)
  
    with open(file_path, 'w') as json_file:
        json.dump(existing_data, json_file, indent=2)

        

if __name__ == '__main__':
    os.makedirs('storage', exist_ok=True)

    socket_thread = threading.Thread(target=run_socket_server, args=(UDP_IP, socket_port))
    socket_thread.start()

    app.run(debug=True, port=web_port, use_reloader=False)

