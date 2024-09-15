from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SelectedStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(50), unique=True, nullable=False)
