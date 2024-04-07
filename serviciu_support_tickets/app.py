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

class SupportTicket(db.Model):
    __tablename__ = 'supporttickets'
    __table_args__ = {'schema': 'asiguraez'}

    ticket_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(50))
    assigned_to = db.Column(db.Integer,nullable=False)
    resolution = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def json_ticket(self):
        return {
            'ticket_id': self.ticket_id,
            'user_id': self.user_id,
            'subject': self.subject,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'assigned_to': self.assigned_to,
            'resolution': self.resolution,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@app.route('/support_tickets', methods=['GET'])
def get_support_tickets():
    try:
        support_tickets = SupportTicket.query.all()
        return make_response(jsonify([ticket.json_ticket() for ticket in support_tickets]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting support tickets: {str(e)}'}), 500)

@app.route('/support_tickets/<int:ticket_id>', methods=['GET'])
def get_support_ticket(ticket_id):
    try:
        support_ticket = SupportTicket.query.get(ticket_id)
        if support_ticket:
            return make_response(jsonify(support_ticket.json_ticket()), 200)
        else:
            return make_response(jsonify({'message': 'Support ticket not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting support ticket: {str(e)}'}), 500)

@app.route('/support_tickets', methods=['POST'])
def add_support_ticket():
    try:
        data = request.get_json()

        new_support_ticket = SupportTicket(
            user_id=data.get('user_id'),
            subject=data['subject'],
            description=data['description'],
            status=data['status'],
            priority=data.get('priority'),
            assigned_to=data.get('assigned_to'),
            resolution=data.get('resolution')
        )

        db.session.add(new_support_ticket)
        db.session.commit()

        return make_response(jsonify({'message': 'Support ticket added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding support ticket: {str(e)}'}), 500)

@app.route('/support_tickets/<int:ticket_id>', methods=['PUT'])
def update_support_ticket(ticket_id):
    try:
        support_ticket = SupportTicket.query.get(ticket_id)
        if not support_ticket:
            return make_response(jsonify({'message': 'Support ticket not found'}), 404)

        data = request.get_json()

        support_ticket.user_id = data.get('user_id', support_ticket.user_id)
        support_ticket.subject = data.get('subject', support_ticket.subject)
        support_ticket.description = data.get('description', support_ticket.description)
        support_ticket.status = data.get('status', support_ticket.status)
        support_ticket.priority = data.get('priority', support_ticket.priority)
        support_ticket.assigned_to = data.get('assigned_to', support_ticket.assigned_to)
        support_ticket.resolution = data.get('resolution', support_ticket.resolution)

        db.session.commit()

        return make_response(jsonify({'message': 'Support ticket updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating support ticket: {str(e)}'}), 500)

@app.route('/support_tickets/<int:ticket_id>', methods=['DELETE'])
def delete_support_ticket(ticket_id):
    try:
        support_ticket = SupportTicket.query.get(ticket_id)
        if not support_ticket:
            return make_response(jsonify({'message': 'Support ticket not found'}), 404)

        db.session.delete(support_ticket)
        db.session.commit()

        return make_response(jsonify({'message': 'Support ticket deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting support ticket: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True)