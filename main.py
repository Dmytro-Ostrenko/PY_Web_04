from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import socket
import json
from datetime import datetime
import threading
import os
import time

app = Flask(__name__)

web_port = 3000
socket_port = 5000
UDP_IP = '127.0.0.1'

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
            print(f'Получено сообщение: {data.decode()} от: {address}')
            sock.sendto(data, address)
            print(f'Отправлено сообщение: {data.decode()} по адресу: {address}')
            decoded_data = json.loads(data.decode('utf-8'))
            save_to_json(decoded_data)

    except KeyboardInterrupt:
        print(f'Остановка сервера')
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
        
def save_to_json(data):
    with open('storage/data.json', 'a') as json_file:
        json.dump(data, json_file)
        json_file.write('\n')



if __name__ == '__main__':
    os.makedirs('storage', exist_ok=True)

    socket_thread = threading.Thread(target=run_socket_server, args=(UDP_IP, socket_port))
    socket_thread.start()

    app.run(debug=True, port=web_port, use_reloader=False)
