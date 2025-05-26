from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Заміни на надійний секрет

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:11111111@localhost/pet_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- МОДЕЛІ ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# --- СТАРТ ---
if __name__ == '__main__':
    app.run(debug=True)
