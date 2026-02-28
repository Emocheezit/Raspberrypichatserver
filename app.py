from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pi_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    # This broadcasts the message to EVERYONE connected
    send(msg, broadcast=True)

@socketio.on('join')
def on_join(username):
    print(f"{username} has joined the lobby")
    emit('message', f"System: {username} entered the chat", broadcast=True)

if __name__ == '__main__':
    # '0.0.0.0' allows other devices on your network to connect
    socketio.run(app, host='0.0.0.0', port=5000)
