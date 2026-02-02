from flask import Flask, session, render_template_string, redirect, url_for, request
from flask_socketio import SocketIO, emit
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

users = {}

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', 'YOUR_GOOGLE_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={'scope': 'email profile'},
    fetch_token=lambda: session.get('token')
)

@app.route('/')
def home():
    user = session.get('user')
    if not user:
        return '<h1>Chat</h1><a href="/login">Login with Google</a>'
    
    return render_template_string('''
<h1>Chat - {{user.name}}</h1>
<div id="messages" style="border:1px solid #ccc;height:300px;overflow-y:scroll;padding:10px;"></div>
<input type="text" id="msg" placeholder="Type message...">
<button onclick="send()">Send</button>
<a href="/logout">Logout</a>
<h3>Online: <span id="count">0</span></h3>
<div id="users"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
<script>
const socket = io();
const msg = document.getElementById('msg');
const messages = document.getElementById('messages');
const usersDiv = document.getElementById('users');
const count = document.getElementById('count');

const user = {name: '{{user.name}}', id: '{{user.id}}'};

function send() {
    if (msg.value.trim()) {
        socket.emit('msg', {text: msg.value, user: user});
        msg.value = '';
    }
}

msg.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') send();
});

socket.on('connect', () => {
    socket.emit('join', user);
});

socket.on('msg', (data) => {
    messages.innerHTML += '<div><b>' + data.user.name + ':</b> ' + data.text + '</div>';
    messages.scrollTop = messages.scrollHeight;
});

socket.on('users', (data) => {
    usersDiv.innerHTML = data.map(u => '<div>' + u + '</div>').join('');
    count.textContent = data.length;
});
</script>
    ''', user=user)

@app.route('/login')
def login():
    return google.authorize_redirect(url_for('auth', _external=True))

@app.route('/auth')
def auth():
    try:
        token = google.authorize_access_token()
        session['token'] = token
        user_info = google.get('userinfo', token=token).json()
        if user_info:
            session['user'] = user_info
            return redirect('/')
    except Exception as e:
        print(f"Auth error: {e}")
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
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    print(f"Starting chat on http://127.0.0.1:{port}")
    socketio.run(app, host='127.0.0.1', port=port, debug=debug)