from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from datetime import datetime
from flask_bcrypt import Bcrypt
import sys
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter  import PrometheusMetrics
from marshmallow import Schema, fields, validate
from dotenv import load_dotenv


sys.path.append('../')

from jwt_required.auth_token import jwt_auth

app = Flask(__name__)
bcrypt = Bcrypt(app)
cache = Cache(app)
limiter = Limiter(get_remote_address,app=app)
metrics = PrometheusMetrics(app)
CORS(app)

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#change this
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')

db = SQLAlchemy(app)

class Policy(db.Model):
    __tablename__ = 'policies'
    __table_args__ = {'schema': 'asiguraez'}

    policy_id = db.Column(db.Integer, primary_key=True)
    policy_name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    coverage_amount = db.Column(db.Numeric(15, 2), nullable=False)
    premium_amount = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    policy_type_id = db.Column(db.Integer, nullable=False)
    insured_id = db.Column(db.Integer, nullable=False)

    def json_policy(self):
        return {
            'policy_id': self.policy_id,
            'policy_name': self.policy_name,
            'description': self.description,
            'coverage_amount': float(self.coverage_amount),
            'premium_amount': float(self.premium_amount),
            'created_at': self.created_at.isoformat(),
            'policy_type_id': self.policy_type_id,
            'insured_id': self.insured_id
        }
    
class PolicySchema(Schema):
    policy_name = fields.Str(required=True,validate=validate.Length(max=255))
    description = fields.Str()
    coverage_amount = fields.Decimal(required=True,places=2)
    premium_amount = fields.Decimal(required=True, places=2)
    created_at =  fields.DateTime(dump_only=True)
    policy_type_id = fields.Integer(required=True)
    insured_id =  fields.Integer(required=True)  


@app.route('/policies', methods=['GET'])
@cache.cached(timeout=360)
def get_policies():
    try:
        page = int(request.args.get('page',1))
        per_page = int(request.args.get('per_page',5))
        policies_pagination = Policy.query.paginate(page=page, per_page=per_page)
        policies = [policy.json_policy() for policy in policies_pagination.items]

        return make_response(jsonify({
            'policies': policies,
            'pages' : policies_pagination.pages,
            'total_policies' : policies_pagination.total
        }),200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting policies: {str(e)}'}), 500)

@app.route('/policies/<int:policy_id>', methods=['GET'])
def get_policy(policy_id):
    try:
        policy = Policy.query.get(policy_id)
        if policy:
            return make_response(jsonify(policy.json_policy()), 200)
        else:
            return make_response(jsonify({'message': 'Policy not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting policy: {str(e)}'}), 500)

@app.route('/policies', methods=['POST'])
@limiter.limit("5 per minute")
def add_policy():
    try:
        data = request.get_json()

        errors = PolicySchema().validate(data)
        if errors:
            return make_response(jsonify({'message':'Validation error', 'errors' : errors}))

        existing_policy = Policy.query.filter_by(policy_name = data['policy_name']).first()
        if existing_policy:
            return make_response(jsonify({'message':' Policy name already exists!'}))
        new_policy = Policy(
            policy_name=data['policy_name'],
            description=data.get('description'),
            coverage_amount=data['coverage_amount'],
            premium_amount=data['premium_amount'],
            policy_type_id=data.get('policy_type_id'),
            insured_id=data.get('insured_id')
        )

        db.session.add(new_policy)
        db.session.commit()

        return make_response(jsonify({'message': 'Policy added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding policy: {str(e)}'}), 500)

@app.route('/policies/<int:policy_id>', methods=['PUT'])
@jwt_auth
def update_policy(policy_id):
    try:
        policy = Policy.query.get(policy_id)
        if not policy:
            return make_response(jsonify({'message': 'Policy not found'}), 404)

        data = request.get_json()

        errors = PolicySchema().validate(data)
        if errors:
            return make_response(jsonify({'message':'Validation error', 'errors' : errors}))

        policy.policy_name = data.get('policy_name', policy.policy_name)
        policy.description = data.get('description', policy.description)
        policy.coverage_amount = data.get('coverage_amount', policy.coverage_amount)
        policy.premium_amount = data.get('premium_amount', policy.premium_amount)
        policy.policy_type_id = data.get('policy_type_id', policy.policy_type_id)
        policy.insured_id = data.get('insured_id', policy.insured_id)

        db.session.commit()

        return make_response(jsonify({'message': 'Policy updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating policy: {str(e)}'}), 500)

@app.route('/policies/<int:policy_id>', methods=['DELETE'])
@jwt_auth
def delete_policy(policy_id):
    try:
        policy = Policy.query.get(policy_id)
        if not policy:
            return make_response(jsonify({'message': 'Policy not found'}), 404)

        db.session.delete(policy)
        db.session.commit()

        return make_response(jsonify({'message': 'Policy deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting policy: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True)  
