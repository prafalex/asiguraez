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

class CoverageType(db.Model):
    __tablename__ = 'coveragetypes'
    __table_args__ = {'schema': 'asiguraez'}

    coverage_id = db.Column(db.Integer, primary_key=True)
    coverage_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    def json_coverage_type(self):
        return {
            'coverage_id': self.coverage_id,
            'coverage_name': self.coverage_name,
            'description': self.description
        }

@app.route('/coverage_types', methods=['GET'])
def get_coverage_types():
    try:
        coverage_types = CoverageType.query.all()
        return make_response(jsonify([coverage_type.json_coverage_type() for coverage_type in coverage_types]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting coverage types: {str(e)}'}), 500)

@app.route('/coverage_types/<int:coverage_id>', methods=['GET'])
def get_coverage_type(coverage_id):
    try:
        coverage_type = CoverageType.query.get(coverage_id)
        if coverage_type:
            return make_response(jsonify(coverage_type.json_coverage_type()), 200)
        else:
            return make_response(jsonify({'message': 'Coverage type not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting coverage type: {str(e)}'}), 500)

@app.route('/coverage_types', methods=['POST'])
def add_coverage_type():
    try:
        data = request.get_json()

        new_coverage_type = CoverageType(
            coverage_name=data['coverage_name'],
            description=data.get('description')
        )

        db.session.add(new_coverage_type)
        db.session.commit()

        return make_response(jsonify({'message': 'Coverage type added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding coverage type: {str(e)}'}), 500)

@app.route('/coverage_types/<int:coverage_id>', methods=['PUT'])
def update_coverage_type(coverage_id):
    try:
        coverage_type = CoverageType.query.get(coverage_id)
        if not coverage_type:
            return make_response(jsonify({'message': 'Coverage type not found'}), 404)

        data = request.get_json()

        coverage_type.coverage_name = data.get('coverage_name', coverage_type.coverage_name)
        coverage_type.description = data.get('description', coverage_type.description)

        db.session.commit()

        return make_response(jsonify({'message': 'Coverage type updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating coverage type: {str(e)}'}), 500)

@app.route('/coverage_types/<int:coverage_id>', methods=['DELETE'])
def delete_coverage_type(coverage_id):
    try:
        coverage_type = CoverageType.query.get(coverage_id)
        if not coverage_type:
            return make_response(jsonify({'message': 'Coverage type not found'}), 404)

        db.session.delete(coverage_type)
        db.session.commit()

        return make_response(jsonify({'message': 'Coverage type deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting coverage type: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True) 