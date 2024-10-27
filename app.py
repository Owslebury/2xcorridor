from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    combination = db.Column(db.String(20), unique=True, nullable=False)  # Limit to 20 characters
    note = db.Column(db.String(200), nullable=False)
    ip = db.Column(db.String(45), nullable=False)  # Store the IP address
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Add created_at field

# Create the database and tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_note', methods=['POST'])
def save_note():
    data = request.json
    combination = data['combination']
    note_text = data['note']
    
    # Automatically retrieve the client IP address
    ip = request.remote_addr  # Get the IP address from the request

    # Check if the combination length exceeds 20 characters
    if len(combination) > 20:
        return jsonify({'success': False, 'message': 'Combination cannot exceed 20 digits.'}), 400

    # Check if the combination already exists
    if Note.query.filter_by(combination=combination).first():
        return jsonify({'success': False, 'message': 'Note already exists for this combination.'}), 400
    
    # Check if there is already a note from the same IP address
    if Note.query.filter_by(ip=ip).first():
        return jsonify({'success': False, 'message': 'You cannot post more than one note from the same IP address.'}), 400

    # Create and save the new note
    new_note = Note(combination=combination, note=note_text, ip=ip)
    db.session.add(new_note)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/get_notes', methods=['GET'])
def get_notes():
    combination = request.args.get('combination')
    note = Note.query.filter_by(combination=combination).first()
    
    if note:
        return jsonify({
            'note': note.note,
            'ip': note.ip,
            'created_at': note.created_at.strftime("%d/%m/%Y %H:%M:%S")  # Format the datetime
        })
    else:
        return jsonify({'note': None, 'ip': None, 'created_at': None})

if __name__ == '__main__':
    app.run(debug=True)
