
from datetime import datetime
from app.database import db

class Contract(db.Model):
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='non_inviato')  # non_inviato, inviato, firmato
    contract_number = db.Column(db.String(50), unique=True)
    sent_date = db.Column(db.DateTime)
    signed_date = db.Column(db.DateTime)
    received_date = db.Column(db.DateTime)
    contract_file_path = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Contract {self.contract_number}>'
