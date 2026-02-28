from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = 'pi_chat_secret'
# High buffer size for those Base64 profile pictures
socketio = SocketIO(app, cors_allowed_origins=["http://dachatthang.chat", "http://localhost:5000"], max_http_buffer_size=1e7)

# Maps username -> { 'sid': session_id, 'pfp': profile_picture_data }
active_users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    # data can be a string (username) or a dict {'username': '...', 'pfp': '...'}
    if isinstance(data, str):
        username = data
        pfp = None
    else:
        username = data.get('username')
        pfp = data.get('pfp')

    # Store user info
    active_users[username] = {
        'sid': request.sid,
        'pfp': pfp
    }
    
    join_room(username)
    print(f"User {username} joined with a custom PFP.")
    
    # Notify everyone that a new user is online
    emit('message', f"{username} joined the lobby", broadcast=True)
    
    # Optional: Broadcast updated user list to keep sidebars in sync
    # emit('user_list', list(active_users.keys()), broadcast=True)

@socketio.on('message')
def handle_message(data):
    # Broadcast the message object (text, user, pfp) to the lobby
    emit('message', data, broadcast=True)

@socketio.on('private_message')
def handle_private_message(data):
    recipient = data['recipient']
    # If the recipient is online, send them the message
    if recipient in active_users:
        emit('new_private_msg', {
            'sender': data['sender'],
            'msg': data['msg'],
            'pfp': data['pfp']
        }, room=active_users[recipient]['sid'])

@socketio.on('friend_request')
def handle_friend_request(data):
    target = data['to']
    if target in active_users:
        # We send the requester's PFP too so the "Accept" button looks cool
        emit('receive_request', {
            'from': data['from'],
            'pfp': active_users.get(data['from'], {}).get('pfp')
        }, room=active_users[target]['sid'])

@socketio.on('disconnect')
def on_disconnect():
    user_to_remove = None
    for user, info in active_users.items():
        if info['sid'] == request.sid:
            user_to_remove = user
            break
            
    if user_to_remove:
        del active_users[user_to_remove]
        print(f"{user_to_remove} went offline.")

if __name__ == '__main__':
    # '0.0.0.0' makes it accessible to any device on your local network
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)