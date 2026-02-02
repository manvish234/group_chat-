import os
from flask import Flask, session, redirect, url_for, request, jsonify, render_template_string
from authlib.integrations.flask_client import OAuth
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret')

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

def init_db():
    conn = sqlite3.connect('/tmp/chat.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS messages 
                    (id INTEGER PRIMARY KEY, user TEXT, message TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    user = session.get('user')
    if not user:
        return '''<html><body style="font-family:Arial;text-align:center;padding:100px;background:#25d366;">
        <div style="background:white;padding:50px;border-radius:20px;max-width:400px;margin:0 auto;">
        <h1>💬 Group Chat</h1>
        <a href="/login" style="background:#075e54;color:white;padding:15px 30px;text-decoration:none;border-radius:25px;">Login with Google</a>
        </div></body></html>'''
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>Group Chat</title>
<style>
body { font-family: Arial; margin: 0; background: #e5ddd5; }
.container { max-width: 800px; margin: 0 auto; padding: 20px; }
.header { background: #075e54; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
.messages { background: white; height: 400px; overflow-y: auto; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
.message { margin-bottom: 10px; padding: 10px; background: #dcf8c6; border-radius: 10px; }
.sender { font-weight: bold; color: #075e54; }
.input-area { display: flex; gap: 10px; }
#msg { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; }
.send-btn { background: #25d366; color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; }
</style>
</head>
<body>
<div class="container">
<div class="header">
<h2>💬 Group Chat - Welcome {{user.name}}!</h2>
<a href="/logout" style="color: white; float: right;">Logout</a>
</div>
<div id="messages" class="messages"></div>
<div class="input-area">
<input type="text" id="msg" placeholder="Type a message...">
<button onclick="sendMessage()" class="send-btn">Send</button>
</div>
</div>

<script>
function loadMessages() {
    fetch('/api/messages')
        .then(r => r.json())
        .then(data => {
            const msgs = document.getElementById('messages');
            msgs.innerHTML = data.map(m => 
                '<div class="message"><div class="sender">' + m.user + '</div>' + m.message + '</div>'
            ).join('');
            msgs.scrollTop = msgs.scrollHeight;
        });
}

function sendMessage() {
    const msg = document.getElementById('msg');
    if (msg.value.trim()) {
        fetch('/api/send', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg.value})
        }).then(() => {
            msg.value = '';
            loadMessages();
        });
    }
}

document.getElementById('msg').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

loadMessages();
setInterval(loadMessages, 2000);
</script>
</body>
</html>
    ''', user=user)

@app.route('/api/messages')
def get_messages():
    init_db()
    conn = sqlite3.connect('/tmp/chat.db')
    messages = conn.execute('SELECT user, message FROM messages ORDER BY timestamp DESC LIMIT 50').fetchall()
    conn.close()
    return jsonify([{'user': m[0], 'message': m[1]} for m in reversed(messages)])

@app.route('/api/send', methods=['POST'])
def send_message():
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    init_db()
    conn = sqlite3.connect('/tmp/chat.db')
    conn.execute('INSERT INTO messages (user, message, timestamp) VALUES (?, ?, ?)',
                (user['name'], data['message'], datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)