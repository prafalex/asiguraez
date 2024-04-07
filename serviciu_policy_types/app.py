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

class PolicyType(db.Model):
    __tablename__ = 'policytypes'
    __table_args__ = {'schema': 'asiguraez'}

    type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    def json_policy_type(self):
        return {
            'type_id': self.type_id,
            'type_name': self.type_name,
            'description': self.description
        }

@app.route('/policytypes', methods=['GET'])
def get_policy_types():
    try:
        policy_types = PolicyType.query.all()
        return make_response(jsonify([policy_type.json_policy_type() for policy_type in policy_types]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting policy types: {str(e)}'}), 500)

@app.route('/policytypes/<int:type_id>', methods=['GET'])
def get_policy_type(type_id):
    try:
        policy_type = PolicyType.query.get(type_id)
        if policy_type:
            return make_response(jsonify(policy_type.json_policy_type()), 200)
        else:
            return make_response(jsonify({'message': 'Policy type not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting policy type: {str(e)}'}), 500)

@app.route('/policytypes', methods=['POST'])
def add_policy_type():
    try:
        data = request.get_json()

        new_policy_type = PolicyType(
            type_name=data['type_name'],
            description=data.get('description')
        )

        db.session.add(new_policy_type)
        db.session.commit()

        return make_response(jsonify({'message': 'Policy type added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding policy type: {str(e)}'}), 500)

@app.route('/policytypes/<int:type_id>', methods=['PUT'])
def update_policy_type(type_id):
    try:
        policy_type = PolicyType.query.get(type_id)
        if not policy_type:
            return make_response(jsonify({'message': 'Policy type not found'}), 404)

        data = request.get_json()

        policy_type.type_name = data.get('type_name', policy_type.type_name)
        policy_type.description = data.get('description', policy_type.description)

        db.session.commit()

        return make_response(jsonify({'message': 'Policy type updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating policy type: {str(e)}'}), 500)

@app.route('/policytypes/<int:type_id>', methods=['DELETE'])
def delete_policy_type(type_id):
    try:
        policy_type = PolicyType.query.get(type_id)
        if not policy_type:
            return make_response(jsonify({'message': 'Policy type not found'}), 404)

        db.session.delete(policy_type)
        db.session.commit()

        return make_response(jsonify({'message': 'Policy type deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting policy type: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True) 
