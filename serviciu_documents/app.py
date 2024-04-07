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

class Document(db.Model):
    __tablename__ = 'documents'
    __table_args__ = {'schema': 'asiguraez'}

    document_id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, nullable=False)
    document_type = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def json_document(self):
        return {
            'document_id': self.document_id,
            'policy_id': self.policy_id,
            'document_type': self.document_type,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat()
        }

@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        documents = Document.query.all()
        return make_response(jsonify([document.json_document() for document in documents]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting documents: {str(e)}'}), 500)

@app.route('/documents/<int:document_id>', methods=['GET'])
def get_document(document_id):
    try:
        document = Document.query.get(document_id)
        if document:
            return make_response(jsonify(document.json_document()), 200)
        else:
            return make_response(jsonify({'message': 'Document not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting document: {str(e)}'}), 500)

@app.route('/documents', methods=['POST'])
def add_document():
    try:
        data = request.get_json()

        new_document = Document(
            policy_id=data['policy_id'],
            document_type=data['document_type'],
            file_path=data['file_path']
        )

        db.session.add(new_document)
        db.session.commit()

        return make_response(jsonify({'message': 'Document added successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error adding document: {str(e)}'}), 500)

@app.route('/documents/<int:document_id>', methods=['PUT'])
def update_document(document_id):
    try:
        document = Document.query.get(document_id)
        if not document:
            return make_response(jsonify({'message': 'Document not found'}), 404)

        data = request.get_json()

        document.policy_id = data.get('policy_id', document.policy_id)
        document.document_type = data.get('document_type', document.document_type)
        document.file_path = data.get('file_path', document.file_path)

        db.session.commit()

        return make_response(jsonify({'message': 'Document updated successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating document: {str(e)}'}), 500)

@app.route('/documents/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    try:
        document = Document.query.get(document_id)
        if not document:
            return make_response(jsonify({'message': 'Document not found'}), 404)

        db.session.delete(document)
        db.session.commit()

        return make_response(jsonify({'message': 'Document deleted successfully'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting document: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True)