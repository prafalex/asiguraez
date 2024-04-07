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

class Claim(db.Model):
    __tablename__ = 'claims'
    __table_args__ = {'schema': 'asiguraez'}

    claim_id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, nullable=False)
    claim_date = db.Column(db.Date, nullable=False)
    claim_amount = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def json_claim(self):
        return {
            'claim_id': self.claim_id,
            'policy_id': self.policy_id,
            'claim_date': self.claim_date.isoformat(),
            'claim_amount': float(self.claim_amount),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

@app.route('/claims', methods=['GET'])
def get_claims():
    try:
        claims = Claim.query.all()
        return make_response(jsonify([claim.json_claim() for claim in claims]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting claims: {str(e)}'}), 500)

@app.route('/claims/<int:claim_id>', methods=['GET'])
def get_claim(claim_id):
    try:
        claim = Claim.query.get(claim_id)
        if claim:
            return make_response(jsonify(claim.json_claim()), 200)
        else:
            return make_response(jsonify({'message': 'Claim not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting claim: {str(e)}'}), 500)

@app.route('/claims', methods=['POST'])
def add_claim():
    try:
        data = request.get_json()

        new_claim = Claim(
            policy_id=data['policy_id'],
            claim_date=datetime.strptime(data['claim_date'], '%Y-%m-%d').date(),
            claim_amount=data['claim_amount'],
            status=data['status']
        )

        db.session.add(new_claim)
        db.session.commit()

        return make_response(jsonify({'message': 'Claim added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding claim: {str(e)}'}), 500)

@app.route('/claims/<int:claim_id>', methods=['PUT'])
def update_claim(claim_id):
    try:
        claim = Claim.query.get(claim_id)
        if not claim:
            return make_response(jsonify({'message': 'Claim not found'}), 404)

        data = request.get_json()

        claim.policy_id = data.get('policy_id', claim.policy_id)
        claim.claim_date = data.get('claim_date', claim.claim_date)
        claim.claim_amount = data.get('claim_amount', claim.claim_amount)
        claim.status = data.get('status', claim.status)

        db.session.commit()

        return make_response(jsonify({'message': 'Claim updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating claim: {str(e)}'}), 500)

@app.route('/claims/<int:claim_id>', methods=['DELETE'])
def delete_claim(claim_id):
    try:
        claim = Claim.query.get(claim_id)
        if not claim:
            return make_response(jsonify({'message': 'Claim not found'}), 404)

        db.session.delete(claim)
        db.session.commit()

        return make_response(jsonify({'message': 'Claim deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting claim: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True)