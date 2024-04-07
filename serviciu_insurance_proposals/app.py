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

class InsuranceProposal(db.Model):
    __tablename__ = 'insuranceproposals'
    __table_args__ = {'schema': 'asiguraez'}

    proposal_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer,nullable=False)
    insured_id = db.Column(db.Integer, nullable=False)
    policy_type_id = db.Column(db.Integer, nullable=False)
    coverage_amount = db.Column(db.Numeric(15, 2), nullable=False)
    premium_amount = db.Column(db.Numeric(15, 2), nullable=False)
    additional_information = db.Column(db.Text)
    proposal_date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)
    policy_id = db.Column(db.Integer)

    def json_insurance_proposal(self):
        return {
            'proposal_id': self.proposal_id,
            'employee_id': self.employee_id,
            'insured_id': self.insured_id,
            'policy_type_id': self.policy_type_id,
            'coverage_amount': str(self.coverage_amount),
            'premium_amount': str(self.premium_amount),
            'additional_information': self.additional_information,
            'proposal_date': self.proposal_date.isoformat(),
            'status': self.status,
            'policy_id': self.policy_id
        }

@app.route('/insurance_proposals', methods=['GET'])
def get_insurance_proposals():
    try:
        insurance_proposals = InsuranceProposal.query.all()
        return make_response(jsonify([proposal.json_insurance_proposal() for proposal in insurance_proposals]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting insurance proposals: {str(e)}'}), 500)

@app.route('/insurance_proposals/<int:proposal_id>', methods=['GET'])
def get_insurance_proposal(proposal_id):
    try:
        insurance_proposal = InsuranceProposal.query.get(proposal_id)
        if insurance_proposal:
            return make_response(jsonify(insurance_proposal.json_insurance_proposal()), 200)
        else:
            return make_response(jsonify({'message': 'Insurance proposal not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting insurance proposal: {str(e)}'}), 500)

@app.route('/insurance_proposals', methods=['POST'])
def add_insurance_proposal():
    try:
        data = request.get_json()

        new_insurance_proposal = InsuranceProposal(
            employee_id=data['employee_id'],
            insured_id=data['insured_id'],
            policy_type_id=data['policy_type_id'],
            coverage_amount=data['coverage_amount'],
            premium_amount=data['premium_amount'],
            additional_information=data.get('additional_information'),
            status=data['status']
        )

        db.session.add(new_insurance_proposal)
        db.session.commit()

        return make_response(jsonify({'message': 'Insurance proposal added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding insurance proposal: {str(e)}'}), 500)

@app.route('/insurance_proposals/<int:proposal_id>', methods=['PUT'])
def update_insurance_proposal(proposal_id):
    try:
        insurance_proposal = InsuranceProposal.query.get(proposal_id)
        if not insurance_proposal:
            return make_response(jsonify({'message': 'Insurance proposal not found'}), 404)

        data = request.get_json()

        insurance_proposal.employee_id = data.get('employee_id', insurance_proposal.employee_id)
        insurance_proposal.insured_id = data.get('insured_id', insurance_proposal.insured_id)
        insurance_proposal.policy_type_id = data.get('policy_type_id', insurance_proposal.policy_type_id)
        insurance_proposal.coverage_amount = data.get('coverage_amount', insurance_proposal.coverage_amount)
        insurance_proposal.premium_amount = data.get('premium_amount', insurance_proposal.premium_amount)
        insurance_proposal.additional_information = data.get('additional_information', insurance_proposal.additional_information)
        insurance_proposal.status = data.get('status', insurance_proposal.status)
        insurance_proposal.policy_id = data.get('policy_id', insurance_proposal.policy_id)

        db.session.commit()

        return make_response(jsonify({'message': 'Insurance proposal updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating insurance proposal: {str(e)}'}), 500)

@app.route('/insurance_proposals/<int:proposal_id>', methods=['DELETE'])
def delete_insurance_proposal(proposal_id):
    try:
        insurance_proposal = InsuranceProposal.query.get(proposal_id)
        if not insurance_proposal:
            return make_response(jsonify({'message': 'Insurance proposal not found'}), 404)

        db.session.delete(insurance_proposal)
        db.session.commit()

        return make_response(jsonify({'message': 'Insurance proposal deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting insurance proposal: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True)