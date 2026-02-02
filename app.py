import os
from flask import Flask, session, redirect, url_for, request
from flask_socketio import SocketIO, emit
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret')
socketio = SocketIO(app)
users = {}

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={'scope': 'email profile'}
)

@app.route('/')
def home():
    user = session.get('user')
    if not user:
        return '''<html><body style="font-family:Arial;text-align:center;padding:100px;background:#25d366;">
        <div style="background:white;padding:50px;border-radius:20px;max-width:400px;margin:0 auto;">
        <h1>💬 WhatsApp Chat</h1>
        <a href="/login" style="background:#075e54;color:white;padding:15px 30px;text-decoration:none;border-radius:25px;">Login with Google</a>
        </div></body></html>'''
    return f'''
<!DOCTYPE html>
<html>
<head><title>WhatsApp Chat</title>
<style>
body {{ font-family: Arial; margin: 0; background: #e5ddd5; }}
.container {{ display: flex; height: 100vh; max-width: 1200px; margin: 0 auto; }}
.sidebar {{ width: 300px; background: #075e54; color: white; }}
.header {{ background: #128c7e; padding: 20px; display: flex; align-items: center; gap: 10px; }}
.profile-pic {{ width: 40px; height: 40px; border-radius: 50%; }}
.logout {{ margin-left: auto; background: #25d366; padding: 5px 10px; border-radius: 15px; text-decoration: none; color: white; font-size: 12px; }}
.users-section {{ padding: 20px; }}
.user-item {{ padding: 8px 0; border-bottom: 1px solid #128c7e; }}
.chat-area {{ flex: 1; display: flex; flex-direction: column; background: white; }}
.chat-header {{ background: #075e54; color: white; padding: 15px; text-align: center; }}
.messages {{ flex: 1; padding: 20px; overflow-y: auto; background: #e5ddd5; }}
.message {{ margin-bottom: 10px; }}
.message-bubble {{ background: #dcf8c6; padding: 8px 12px; border-radius: 10px; max-width: 70%; display: inline-block; }}
.sender {{ font-weight: bold; color: #075e54; font-size: 14px; }}
.input-area {{ padding: 15px; background: #f0f0f0; display: flex; gap: 10px; }}
#msg {{ flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; outline: none; }}
.send-btn {{ background: #25d366; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; }}
.online-count {{ background: #25d366; color: white; padding: 3px 8px; border-radius: 10px; font-size: 12px; }}
</style>
</head>
<body>
<div class="container">
<div class="sidebar">
<div class="header">
<img src="{user.get('picture', '')}" class="profile-pic">
<div>
<div>{user['name']}</div>
<a href="/logout" class="logout">Logout</a>
</div>
</div>
<div class="users-section">
<h3>Online <span id="count" class="online-count">0</span></h3>
<div id="users"></div>
</div>
</div>
<div class="chat-area">
<div class="chat-header"><h2>💬 Group Chat</h2></div>
<div id="messages" class="messages"></div>
<div class="input-area">
<input type="text" id="msg" placeholder="Type a message...">
<button onclick="send()" class="send-btn">Send</button>
</div>
</div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
<script>
const socket = io();
const msg = document.getElementById('msg');
const messages = document.getElementById('messages');
const usersDiv = document.getElementById('users');
const count = document.getElementById('count');
const user = {{name: '{user["name"]}', id: '{user["id"]}'}};

function send() {{
    if (msg.value.trim()) {{
        socket.emit('msg', {{text: msg.value, user: user}});
        msg.value = '';
    }}
}}
msg.addEventListener('keypress', (e) => {{ if (e.key === 'Enter') send(); }});
socket.on('connect', () => {{ socket.emit('join', user); }});
socket.on('msg', (data) => {{
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.innerHTML = '<div class="message-bubble"><div class="sender">' + data.user.name + '</div>' + data.text + '</div>';
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}});
socket.on('users', (data) => {{
    usersDiv.innerHTML = data.map(u => '<div class="user-item">' + u + '</div>').join('');
    count.textContent = data.length;
}});
</script>
    '''

@app.route('/login')
def login():
    return google.authorize_redirect(url_for('auth', _external=True))

@app.route('/auth')
def auth():
    try:
        token = google.authorize_access_token()
        user_info = google.get('userinfo').json()
        if user_info:
            session['user'] = user_info
            return redirect('/')
    except:
        pass
    return 'Login failed'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@socketio.on('join')
def join(user):
    users[request.sid] = user['name']
    emit('users', list(users.values()), broadcast=True)
    print(f"Connected: {user['name']}")

@socketio.on('disconnect')
def disconnect():
    if request.sid in users:
        name = users[request.sid]
        del users[request.sid]
        emit('users', list(users.values()), broadcast=True)
        print(f"Disconnected: {name}")

@socketio.on('msg')
def handle_msg(data):
    emit('msg', data, broadcast=True)
    print(f"{data['user']['name']}: {data['text']}")

if __name__ == '__main__':
    print("Starting chat on http://127.0.0.1:8000")
    socketio.run(app, host='127.0.0.1', port=8000, debug=True)
else:
    # For Vercel deployment
    app = app
