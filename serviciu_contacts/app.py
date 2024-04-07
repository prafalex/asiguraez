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

class Contact(db.Model):
    __tablename__ = 'contacts'
    __table_args__ = {'schema': 'asiguraez'}

    contact_id = db.Column(db.Integer, primary_key=True)
    insured_id = db.Column(db.Integer, nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def json_contact(self):
        return {
            'contact_id': self.contact_id,
            'insured_id': self.insured_id,
            'contact_name': self.contact_name,
            'relationship': self.relationship,
            'phone_number': self.phone_number,
            'created_at': self.created_at.isoformat()
        }

@app.route('/contacts', methods=['GET'])
def get_contacts():
    try:
        contacts = Contact.query.all()
        return make_response(jsonify([contact.json_contact() for contact in contacts]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting contacts: {str(e)}'}), 500)

@app.route('/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    try:
        contact = Contact.query.get(contact_id)
        if contact:
            return make_response(jsonify(contact.json_contact()), 200)
        else:
            return make_response(jsonify({'message': 'Contact not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting contact: {str(e)}'}), 500)

@app.route('/contacts', methods=['POST'])
def add_contact():
    try:
        data = request.get_json()

        new_contact = Contact(
            insured_id=data['insured_id'],
            contact_name=data['contact_name'],
            relationship=data['relationship'],
            phone_number=data['phone_number']
        )

        db.session.add(new_contact)
        db.session.commit()

        return make_response(jsonify({'message': 'Contact added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding contact: {str(e)}'}), 500)

@app.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            return make_response(jsonify({'message': 'Contact not found'}), 404)

        data = request.get_json()

        contact.insured_id = data.get('insured_id', contact.insured_id)
        contact.contact_name = data.get('contact_name', contact.contact_name)
        contact.relationship = data.get('relationship', contact.relationship)
        contact.phone_number = data.get('phone_number', contact.phone_number)

        db.session.commit()

        return make_response(jsonify({'message': 'Contact updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating contact: {str(e)}'}), 500)

@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            return make_response(jsonify({'message': 'Contact not found'}), 404)

        db.session.delete(contact)
        db.session.commit()

        return make_response(jsonify({'message': 'Contact deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting contact: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True) 