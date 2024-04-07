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

class Address(db.Model):
    __tablename__ = 'addresses'
    __table_args__ = {'schema': 'asiguraez'}

    address_id = db.Column(db.Integer, primary_key=True)
    insured_id = db.Column(db.Integer,nullable=False)
    address_type = db.Column(db.String(50), nullable=False)
    street_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def json_address(self):
        return {
            'address_id': self.address_id,
            'insured_id': self.insured_id,
            'address_type': self.address_type,
            'street_address': self.street_address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'created_at': self.created_at.isoformat()
        }

@app.route('/addresses', methods=['GET'])
def get_addresses():
    try:
        addresses = Address.query.all()
        return make_response(jsonify([address.json_address() for address in addresses]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting addresses: {str(e)}'}), 500)

@app.route('/addresses/<int:address_id>', methods=['GET'])
def get_address(address_id):
    try:
        address = Address.query.get(address_id)
        if address:
            return make_response(jsonify(address.json_address()), 200)
        else:
            return make_response(jsonify({'message': 'Address not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting address: {str(e)}'}), 500)

@app.route('/addresses', methods=['POST'])
def add_address():
    try:
        data = request.get_json()
        required_fields = ['address_type', 'street_address', 'city', 'state', 'zip_code']
        for field in required_fields:
            if field not in data:
                return make_response(jsonify({'message': f'Missing required field: {field}'}), 400)


        new_address = Address(
            insured_id=data.get('insured_id'),
            address_type=data['address_type'],
            street_address=data['street_address'],
            city=data['city'],
            state=data['state'],
            zip_code=data['zip_code']
        )

        db.session.add(new_address)
        db.session.commit()

        return make_response(jsonify({'message': 'Address added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding address: {str(e)}'}), 500)

@app.route('/addresses/<int:address_id>', methods=['PUT'])
def update_address(address_id):
    try:
        address = Address.query.get(address_id)
        if not address:
            return make_response(jsonify({'message': 'Address not found'}), 404)

        data = request.get_json()

        required_fields = ['address_type', 'street_address', 'city', 'state', 'zip_code']
        for field in required_fields:
            if field not in data:
                return make_response(jsonify({'message': f'Missing required field: {field}'}), 400)


        address.insured_id = data.get('insured_id', address.insured_id)
        address.address_type = data.get('address_type', address.address_type)
        address.street_address = data.get('street_address', address.street_address)
        address.city = data.get('city', address.city)
        address.state = data.get('state', address.state)
        address.zip_code = data.get('zip_code', address.zip_code)

        db.session.commit()

        return make_response(jsonify({'message': 'Address updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating address: {str(e)}'}), 500)

@app.route('/addresses/<int:address_id>', methods=['DELETE'])
def delete_address(address_id):
    try:
        address = Address.query.get(address_id)
        if not address:
            return make_response(jsonify({'message': 'Address not found'}), 404)

        db.session.delete(address)
        db.session.commit()

        return make_response(jsonify({'message': 'Address deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting address: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True) 