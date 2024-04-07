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

class PremiumRate(db.Model):
    __tablename__ = 'premiumrates'
    __table_args__ = {'schema': 'asiguraez'}

    rate_id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, nullable=False)
    coverage_id = db.Column(db.Integer, nullable=False)
    age_range = db.Column(db.String(50), nullable=False)
    rate_amount = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def json_premium_rate(self):
        return {
            'rate_id': self.rate_id,
            'policy_id': self.policy_id,
            'coverage_id': self.coverage_id,
            'age_range': self.age_range,
            'rate_amount': str(self.rate_amount),
            'created_at': self.created_at.isoformat()
        }

@app.route('/premium_rates', methods=['GET'])
def get_premium_rates():
    try:
        premium_rates = PremiumRate.query.all()
        return make_response(jsonify([premium_rate.json_premium_rate() for premium_rate in premium_rates]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting premium rates: {str(e)}'}), 500)

@app.route('/premium_rates/<int:rate_id>', methods=['GET'])
def get_premium_rate(rate_id):
    try:
        premium_rate = PremiumRate.query.get(rate_id)
        if premium_rate:
            return make_response(jsonify(premium_rate.json_premium_rate()), 200)
        else:
            return make_response(jsonify({'message': 'Premium rate not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting premium rate: {str(e)}'}), 500)

@app.route('/premium_rates', methods=['POST'])
def add_premium_rate():
    try:
        data = request.get_json()

        new_premium_rate = PremiumRate(
            policy_id=data['policy_id'],
            coverage_id=data['coverage_id'],
            age_range=data['age_range'],
            rate_amount=data['rate_amount']
        )

        db.session.add(new_premium_rate)
        db.session.commit()

        return make_response(jsonify({'message': 'Premium rate added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding premium rate: {str(e)}'}), 500)

@app.route('/premium_rates/<int:rate_id>', methods=['PUT'])
def update_premium_rate(rate_id):
    try:
        premium_rate = PremiumRate.query.get(rate_id)
        if not premium_rate:
            return make_response(jsonify({'message': 'Premium rate not found'}), 404)

        data = request.get_json()

        premium_rate.policy_id = data.get('policy_id', premium_rate.policy_id)
        premium_rate.coverage_id = data.get('coverage_id', premium_rate.coverage_id)
        premium_rate.age_range = data.get('age_range', premium_rate.age_range)
        premium_rate.rate_amount = data.get('rate_amount', premium_rate.rate_amount)

        db.session.commit()

        return make_response(jsonify({'message': 'Premium rate updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating premium rate: {str(e)}'}), 500)

@app.route('/premium_rates/<int:rate_id>', methods=['DELETE'])
def delete_premium_rate(rate_id):
    try:
        premium_rate = PremiumRate.query.get(rate_id)
        if not premium_rate:
            return make_response(jsonify({'message': 'Premium rate not found'}), 404)

        db.session.delete(premium_rate)
        db.session.commit()

        return make_response(jsonify({'message': 'Premium rate deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting premium rate: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True)