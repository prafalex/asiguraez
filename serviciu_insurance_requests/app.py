from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from datetime import datetime
import sys


app = Flask(__name__)
CORS(app)

sys.path.append('../')

from jwt_required.auth_token import jwt_auth

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://user:user123@localhost:5432/db_asiguraez"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'cheie_secreta'

db = SQLAlchemy(app)

class InsuranceRequest(db.Model):
    __tablename__ = 'insurancerequests'
    __table_args__ = {'schema': 'asiguraez'}

    request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    policy_type_id = db.Column(db.Integer, nullable=False)
    coverage_amount = db.Column(db.Numeric(15, 2), nullable=False)
    additional_information = db.Column(db.Text)
    request_date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)
    policy_id = db.Column(db.Integer)

    def json_insurance_request(self):
        return {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'policy_type_id': self.policy_type_id,
            'coverage_amount': str(self.coverage_amount),
            'additional_information': self.additional_information,
            'request_date': self.request_date.isoformat(),
            'status': self.status,
            'policy_id': self.policy_id
        }

@app.route('/insurance_requests', methods=['GET'])
def get_insurance_requests():
    try:
        insurance_requests = InsuranceRequest.query.all()
        return make_response(jsonify([request.json_insurance_request() for request in insurance_requests]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting insurance requests: {str(e)}'}), 500)

@app.route('/insurance_requests/<int:request_id>', methods=['GET'])
def get_insurance_request(request_id):
    try:
        insurance_request = InsuranceRequest.query.get(request_id)
        if insurance_request:
            return make_response(jsonify(insurance_request.json_insurance_request()), 200)
        else:
            return make_response(jsonify({'message': 'Insurance request not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting insurance request: {str(e)}'}), 500)

@app.route('/insurance_requests', methods=['POST'])
def add_insurance_request():
    try:
        data = request.get_json()

        new_insurance_request = InsuranceRequest(
            user_id=data['user_id'],
            policy_type_id=data['policy_type_id'],
            coverage_amount=data['coverage_amount'],
            additional_information=data.get('additional_information'),
            status=data['status']
        )

        db.session.add(new_insurance_request)
        db.session.commit()

        return make_response(jsonify({'message': 'Insurance request added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding insurance request: {str(e)}'}), 500)

@app.route('/insurance_requests/<int:request_id>', methods=['PUT'])
def update_insurance_request(request_id):
    try:
        insurance_request = InsuranceRequest.query.get(request_id)
        if not insurance_request:
            return make_response(jsonify({'message': 'Insurance request not found'}), 404)

        data = request.get_json()

        insurance_request.user_id = data.get('user_id', insurance_request.user_id)
        insurance_request.policy_type_id = data.get('policy_type_id', insurance_request.policy_type_id)
        insurance_request.coverage_amount = data.get('coverage_amount', insurance_request.coverage_amount)
        insurance_request.additional_information = data.get('additional_information', insurance_request.additional_information)
        insurance_request.status = data.get('status', insurance_request.status)
        insurance_request.policy_id = data.get('policy_id', insurance_request.policy_id)

        db.session.commit()

        return make_response(jsonify({'message': 'Insurance request updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating insurance request: {str(e)}'}), 500)

@app.route('/insurance_requests/<int:request_id>', methods=['DELETE'])
@jwt_auth
def delete_insurance_request(request_id):
    try:
        insurance_request = InsuranceRequest.query.get(request_id)
        if not insurance_request:
            return make_response(jsonify({'message': 'Insurance request not found'}), 404)

        db.session.delete(insurance_request)
        db.session.commit()

        return make_response(jsonify({'message': 'Insurance request deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting insurance request: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True)