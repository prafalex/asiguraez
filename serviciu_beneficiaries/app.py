from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://user:user123@localhost:5432/db_asiguraez"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Beneficiary(db.Model):
    __tablename__ = 'beneficiaries'
    __table_args__ = {'schema': 'asiguraez'}

    beneficiary_id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, nullable=False)
    beneficiary_name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def json_beneficiary(self):
        return {
            'beneficiary_id': self.beneficiary_id,
            'policy_id': self.policy_id,
            'beneficiary_name': self.beneficiary_name,
            'relationship': self.relationship,
            'created_at': self.created_at.isoformat()
        }

@app.route('/beneficiaries', methods=['GET'])
def get_beneficiaries():
    try:
        beneficiaries = Beneficiary.query.all()
        return make_response(jsonify([beneficiary.json_beneficiary() for beneficiary in beneficiaries]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting beneficiaries: {str(e)}'}), 500)

@app.route('/beneficiaries/<int:beneficiary_id>', methods=['GET'])
def get_beneficiary(beneficiary_id):
    try:
        beneficiary = Beneficiary.query.get(beneficiary_id)
        if beneficiary:
            return make_response(jsonify(beneficiary.json_beneficiary()), 200)
        else:
            return make_response(jsonify({'message': 'Beneficiary not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting beneficiary: {str(e)}'}), 500)

@app.route('/beneficiaries', methods=['POST'])
def add_beneficiary():
    try:
        data = request.get_json()

        new_beneficiary = Beneficiary(
            policy_id=data['policy_id'],
            beneficiary_name=data['beneficiary_name'],
            relationship=data['relationship']
        )

        db.session.add(new_beneficiary)
        db.session.commit()

        return make_response(jsonify({'message': 'Beneficiary added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding beneficiary: {str(e)}'}), 500)

@app.route('/beneficiaries/<int:beneficiary_id>', methods=['PUT'])
def update_beneficiary(beneficiary_id):
    try:
        beneficiary = Beneficiary.query.get(beneficiary_id)
        if not beneficiary:
            return make_response(jsonify({'message': 'Beneficiary not found'}), 404)

        data = request.get_json()

        beneficiary.policy_id = data.get('policy_id', beneficiary.policy_id)
        beneficiary.beneficiary_name = data.get('beneficiary_name', beneficiary.beneficiary_name)
        beneficiary.relationship = data.get('relationship', beneficiary.relationship)

        db.session.commit()

        return make_response(jsonify({'message': 'Beneficiary updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating beneficiary: {str(e)}'}), 500)

@app.route('/beneficiaries/<int:beneficiary_id>', methods=['DELETE'])
def delete_beneficiary(beneficiary_id):
    try:
        beneficiary = Beneficiary.query.get(beneficiary_id)
        if not beneficiary:
            return make_response(jsonify({'message': 'Beneficiary not found'}), 404)

        db.session.delete(beneficiary)
        db.session.commit()

        return make_response(jsonify({'message': 'Beneficiary deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting beneficiary: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True) 