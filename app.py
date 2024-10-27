from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    combination = db.Column(db.String(50), unique=True, nullable=False)
    note = db.Column(db.String(200), nullable=False)

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
    
    if Note.query.filter_by(combination=combination).first():
        return jsonify({'success': False, 'message': 'Note already exists for this combination.'}), 400

    new_note = Note(combination=combination, note=note_text)
    db.session.add(new_note)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/get_notes', methods=['GET'])
def get_notes():
    combination = request.args.get('combination')
    note = Note.query.filter_by(combination=combination).first()
    
    if note:
        return jsonify({'note': note.note})
    else:
        return jsonify({'note': None})


if __name__ == '__main__':
    app.run(debug=True)
