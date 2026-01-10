from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import Usuario

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    senha = data.get('senha')

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not usuario.check_password(senha):
        return jsonify({'erro': 'Credenciais inválidas'}), 401

    token = create_access_token(identity=usuario.id)
    return jsonify({'access_token': token}), 200
