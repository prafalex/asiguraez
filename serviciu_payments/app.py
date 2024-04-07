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

class Payment(db.Model):
    __tablename__ = 'payments'
    __table_args__ = {'schema': 'asiguraez'}

    payment_id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def json_payment(self):
        return {
            'payment_id': self.payment_id,
            'policy_id': self.policy_id,
            'payment_date': self.payment_date.isoformat(),
            'amount': float(self.amount),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

@app.route('/payments', methods=['GET'])
def get_payments():
    try:
        payments = Payment.query.all()
        return make_response(jsonify([payment.json_payment() for payment in payments]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting payments: {str(e)}'}), 500)

@app.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    try:
        payment = Payment.query.get(payment_id)
        if payment:
            return make_response(jsonify(payment.json_payment()), 200)
        else:
            return make_response(jsonify({'message': 'Payment not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting payment: {str(e)}'}), 500)

@app.route('/payments', methods=['POST'])
def add_payment():
    try:
        data = request.get_json()

        new_payment = Payment(
            policy_id=data['policy_id'],
            payment_date=data['payment_date'],
            amount=data['amount'],
            status=data['status']
        )

        db.session.add(new_payment)
        db.session.commit()

        return make_response(jsonify({'message': 'Payment added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding payment: {str(e)}'}), 500)

@app.route('/payments/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return make_response(jsonify({'message': 'Payment not found'}), 404)

        data = request.get_json()

        payment.policy_id = data.get('policy_id', payment.policy_id)
        payment.payment_date = data.get('payment_date', payment.payment_date)
        payment.amount = data.get('amount', payment.amount)
        payment.status = data.get('status', payment.status)

        db.session.commit()

        return make_response(jsonify({'message': 'Payment updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating payment: {str(e)}'}), 500)

@app.route('/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return make_response(jsonify({'message': 'Payment not found'}), 404)

        db.session.delete(payment)
        db.session.commit()

        return make_response(jsonify({'message': 'Payment deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting payment: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True) 
