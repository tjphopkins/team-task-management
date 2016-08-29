from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.googlelogin import GoogleLogin
from flask.ext.mongoengine import MongoEngine

from config import SECRET_CONFIG

app = Flask(__name__)

# Configuration
app.config.update(SECRET_CONFIG)
app.config.update(
    MONGODB_SETTINGS={'DB': "todo"},
    DATABASE=MongoEngine(app)
)

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)

# Google Login
googlelogin = GoogleLogin()
googlelogin.init_app(app, login_manager)

if __name__ == '__main__':
    app.run(debug=True)
