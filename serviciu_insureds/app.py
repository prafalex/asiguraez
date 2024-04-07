from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from datetime import datetime
import logging

#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://user:user123@localhost:5432/db_asiguraez"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Insured(db.Model):
    __tablename__ = 'insured'
    __table_args__ = {'schema': 'asiguraez'}

    insured_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,unique=True,nullable=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    occupation = db.Column(db.String(100))
    marital_status = db.Column(db.String(50))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def json_insured(self):
        return {
            'insured_id': self.insured_id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat(),
            'gender': self.gender,
            'occupation': self.occupation,
            'marital_status': self.marital_status,
            'created_at': self.created_at.isoformat()
        }

@app.route('/insured', methods=['GET'])
def get_insureds():
    try:
        insureds = Insured.query.all()
        return make_response(jsonify([insured.json_insured() for insured in insureds]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting insureds: {str(e)}'}), 500)

@app.route('/insured/<int:insured_id>', methods=['GET'])
def get_insured_by_id(insured_id):
    try:
        insured = Insured.query.get(insured_id)
        if insured:
            return make_response(jsonify(insured.json_insured()), 200)
        else:
            return make_response(jsonify({'message': 'Insured not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting insured: {str(e)}'}), 500)

@app.route('/insured', methods=['POST'])
def add_insured():
    try:
        data = request.get_json()

        new_insured = Insured(
            user_id=data['user_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
            gender=data['gender'],
            occupation=data.get('occupation'),
            marital_status=data.get('marital_status')
        )

        db.session.add(new_insured)
        db.session.commit()

        return make_response(jsonify({'message': 'Insured added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding insured: {str(e)}'}), 500)

@app.route('/insured/<int:insured_id>', methods=['PUT'])
def update_insured(insured_id):
    try:
        insured = Insured.query.get(insured_id)
        if not insured:
            return make_response(jsonify({'message': 'Insured not found'}), 404)

        data = request.get_json()

        insured.user_id = data.get('user_id', insured.user_id)
        insured.first_name = data.get('first_name', insured.first_name)
        insured.last_name = data.get('last_name', insured.last_name)
        insured.date_of_birth = datetime.strptime(data.get('date_of_birth', insured.date_of_birth.isoformat()), '%Y-%m-%d').date()
        insured.gender = data.get('gender', insured.gender)
        insured.occupation = data.get('occupation', insured.occupation)
        insured.marital_status = data.get('marital_status', insured.marital_status)

        db.session.commit()

        return make_response(jsonify({'message': 'Insured updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating insured: {str(e)}'}), 500)

@app.route('/insured/<int:insured_id>', methods=['DELETE'])
def delete_insured(insured_id):
    try:
        insured = Insured.query.get(insured_id)
        if not insured:
            return make_response(jsonify({'message': 'Insured not found'}), 404)

        db.session.delete(insured)
        db.session.commit()

        return make_response(jsonify({'message': 'Insured deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting insured: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True) 
