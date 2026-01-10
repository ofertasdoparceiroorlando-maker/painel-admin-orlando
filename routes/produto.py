from flask import Blueprint, request, jsonify
from models import Produto
from extensions import db

produto_bp = Blueprint('produto_bp', __name__)

@produto_bp.route('/', methods=['GET'])
def produto():
    asin = request.args.get('asin')
    if not asin:
        return jsonify({'erro': 'ASIN não fornecido'}), 400

    return jsonify({'asin': asin, 'produto': 'Nome do produto fictício'})

@produto_bp.route('/', methods=['POST'])
def criar_produto():
    print("DEBUG db:", db)  # ✅ Confirmar se db está acessível
    try:
        data = request.get_json() or {}

        asin = data.get('asin')
        nome = data.get('nome')

        if not asin or not nome:
            return jsonify({'erro': 'Campos obrigatórios: asin e nome'}), 400

        if Produto.query.filter_by(asin=asin).first():
            return jsonify({'erro': 'ASIN já cadastrado'}), 409

        produto = Produto(
            asin=asin,
            nome=nome,
            preco=data.get('preco'),
            imagem_url=data.get('imagem_url'),
            rating=data.get('rating')
        )

        db.session.add(produto)
        db.session.commit()

        return jsonify(produto.to_dict()), 201

    except Exception as e:
        return jsonify({'erro': 'Erro interno', 'detalhes': str(e)}), 500
