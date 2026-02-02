# 💬 Real-Time Group Chat

A WhatsApp-style real-time chat application built with Flask, Socket.IO, and Google OAuth.

## ✨ Features

- 🔐 **Google OAuth Authentication** - Secure login with Gmail
- 💬 **Real-time Messaging** - Instant message delivery using WebSockets
- 👥 **Online User Tracking** - See who's currently online
- 🎨 **WhatsApp-style UI** - Clean, modern interface
- 📱 **Responsive Design** - Works on desktop and mobile
- 🔄 **Auto-reconnection** - Handles network interruptions

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Cloud Console project with OAuth credentials

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/manvish234/group_chat.git
   cd group_chat
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python3 app.py
   ```

4. **Open your browser:**
   - Go to `http://127.0.0.1:8000`
   - Login with your Google account
   - Start chatting!

## 🔧 Configuration

### Environment Variables
1. Copy `.env.example` to `.env`
2. Fill in your actual OAuth credentials:
   ```
   GOOGLE_CLIENT_ID=your_google_client_id_here
   GOOGLE_CLIENT_SECRET=your_google_client_secret_here
   SECRET_KEY=your_flask_secret_key_here
   ```

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://127.0.0.1:8000/auth`
6. Update credentials in `app.py`

## 📁 Project Structure

```
group_chat/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
└── chat.db           # SQLite database (auto-created)
```

## 🛠️ Technology Stack

- **Backend:** Flask, Flask-SocketIO
- **Frontend:** HTML, CSS, JavaScript
- **Authentication:** Google OAuth 2.0
- **Real-time:** WebSockets via Socket.IO
- **Database:** SQLite (in-memory for users)

## 🌐 How It Works

### Real-time Communication
- Uses **WebSockets** for bidirectional communication
- **Socket.IO** handles connection management and fallbacks
- **CDN delivery** for fast Socket.IO client loading

### User Management
- **Session-based** authentication with Google OAuth
- **In-memory storage** for online user tracking
- **Automatic cleanup** when users disconnect

### Message Broadcasting
- Messages broadcast to **all connected users**
- **Event-driven architecture** for real-time updates
- **Persistent connections** for instant delivery

## 🔒 Security Features

- Google OAuth 2.0 authentication
- Session management
- Input validation
- CORS protection

## 🚀 Deployment

For production deployment:

1. **Update OAuth credentials** for your domain
2. **Use production WSGI server** (Gunicorn)
3. **Add HTTPS** for secure connections
4. **Use Redis** for session storage in multi-server setup

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

**Manvish** - [GitHub](https://github.com/manvish234)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

**⭐ Star this repository if you found it helpful!**