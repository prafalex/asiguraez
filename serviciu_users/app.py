from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from datetime import datetime,timedelta
from flask_bcrypt import Bcrypt
import jwt
import sys
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter  import PrometheusMetrics
from marshmallow import Schema, fields, validate
from flask_login import LoginManager,UserMixin,login_user,login_required,current_user,logout_user


sys.path.append('../')

from jwt_required.auth_token import jwt_auth

app = Flask(__name__)
bcrypt = Bcrypt(app)
cache = Cache(app)
limiter = Limiter(get_remote_address,app=app)
metrics = PrometheusMetrics(app)
login_manager= LoginManager(app)
CORS(app)


app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://user:user123@localhost:5432/db_asiguraez"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#should be included else where
app.config['SECRET_KEY'] = 'cheie_secreta'

db = SQLAlchemy(app)

def generate_jwt(user_id,role):
    payload ={
        'user_id':user_id,
        'role': role,
        'exp': datetime.now() + timedelta(hours=1)
    }

    token = jwt.encode(payload, app.config['SECRET_KEY'],algorithm='HS256')
    return token

class User(db.Model,UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'asiguraez'}

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    role = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default = True)

    def json_user(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'created_at': self.created_at.isoformat(),
            'role': self.role,
            'is_active': self.is_active
        }

    def get_id(self):
        return str(self.user_id)  
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=255))
    role = fields.Str(validate=validate.OneOf(['admin', 'user','visitor']))
    is_active = fields.Bool()

#pagination added
#cache
@app.route('/users', methods=['GET'])
@cache.cached(timeout=360)
def get_users():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        users_pagination = User.query.paginate(page=page, per_page=per_page)
        users = [user.json_user() for user in users_pagination.items]
        return make_response(jsonify({
            'users': users,
            'pages': users_pagination.pages,
            'total_users': users_pagination.total
        }), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting users: {str(e)}'}), 500)


#limit added
@app.route('/users', methods=['POST'])
@limiter.limit("5 per minute")
def add_user():
    try:
        data = request.get_json()

        errors = UserSchema().validate(data)
        if errors:
            return make_response(jsonify({'message': 'Validation error', 'errors': errors}), 400)


        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return make_response(jsonify({'message': 'Email already in use'}), 400)

        new_user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role')
        )
        new_user.set_password(data['password'])

        db.session.add(new_user)
        db.session.commit()

        return make_response(jsonify({'message': 'User added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding user: {str(e)}'}), 500)


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        user = User.query.get(user_id)
        if user:
            return make_response(jsonify(user.json_user()), 200)
        else:
            return make_response(jsonify({'message': 'User not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting user: {str(e)}'}), 500)

@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_auth
def update_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({'message': 'User not found'}), 404)

        data = request.get_json()

        errors = UserSchema().validate(data)
        if errors:
            return make_response(jsonify({'message': 'Validation error', 'errors': errors}), 400)


        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.password = data.get('password', user.password)
        user.role = data.get('role', user.role)

        db.session.commit()

        return make_response(jsonify({'message': 'User updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating user: {str(e)}'}), 500)



@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_auth
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({'message': 'User not found'}), 404)

        db.session.delete(user)
        db.session.commit()

        return make_response(jsonify({'message': 'User deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting user: {str(e)}'}), 500)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))    

@app.route('/users/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        if not email or not password:
            return make_response(jsonify({'message': 'Email and password are required'}), 400)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return make_response(jsonify({'message': 'Logged in successfully'}), 200)
        else:
            return make_response(jsonify({'message': 'Invalid email or password'}), 401)
    except Exception as e:
        return make_response(jsonify({'message': f'Error logging in: {str(e)}'}), 500)
    
@app.route('/metrics')
def metrics():
    return make_response(metrics.generate_latest(),200)

@app.route('/users/logout')
def logout():
    logout_user()
    return 'Logged out'

@app.route('/protected')
def protected():
    if current_user.is_authenticated:
        return 'Authenticated'
    else:
        return 'Not auth'

if __name__ == '__main__':
    app.run(debug=True)
