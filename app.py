from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dachatthang-secret-123'
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionary to map Username -> Session ID (sid)
# This is the "address book" for DMs
users = {} 

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('connect')
def handle_connect():
    print(f"[+] New connection: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    # Find and remove the user from our address book on disconnect
    disconnected_user = None
    for username, sid in list(users.items()):
        if sid == request.sid:
            disconnected_user = username
            del users[username]
            break
    
    if disconnected_user:
        print(f"[-] {disconnected_user} disconnected")
        send(f"{disconnected_user} has left the chat.", broadcast=True)

@socketio.on('join')
def handle_join(username):
    # Map the current session ID to the chosen username
    users[username] = request.sid
    print(f"[#] {username} joined with SID: {request.sid}")
    send(f"{username} has joined the dachatthang lobby.", broadcast=True)

# --- PUBLIC CHAT HANDLER ---
@socketio.on('message')
def handle_message(msg):
    # Find who sent it based on their SID
    sender = next((u for u, s in users.items() if s == request.sid), "Anonymous")
    print(f"[Lobby] {sender}: {msg}")
    send(f"{sender}: {msg}", broadcast=True)

# --- PRIVATE DM HANDLER ---
@socketio.on('private_message')
def handle_private(data):
    """
    Expects data format: {'recipient': 'Milo', 'msg': 'Hey!'}
    """
    recipient_name = data.get('recipient')
    message_text = data.get('msg')
    sender_name = next((u for u, s in users.items() if s == request.sid), "Anonymous")
    
    # Look up the recipient's "pipe" (SID)
    recipient_sid = users.get(recipient_name)
    
    if recipient_sid:
        # Only send to that specific person's ID
        emit('new_private_msg', {
            'sender': sender_name,
            'msg': message_text
        }, room=recipient_sid)
        print(f"[DM] {sender_name} -> {recipient_name}: {message_text}")
    else:
        # Optional: Send an error back to the sender if user is offline
        emit('message', f"System: {recipient_name} is currently offline.")

if __name__ == '__main__':
    # '0.0.0.0' makes it accessible to anyone on your Wi-Fi
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)