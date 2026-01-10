import csv
from io import StringIO
from datetime import datetime
from flask import Response, Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models import Usuario, Favorito, Oferta, Comentario
from sqlalchemy import desc
from utils.alertas import verificar_alerta_categoria


usuarios_bp = Blueprint('usuarios', __name__)

# Cadastro de usuário
@usuarios_bp.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    dados = request.get_json() or {}
    email = dados.get('email')
    senha = dados.get('senha')
    nome = dados.get('nome')

    if not email or not senha:
        return jsonify({'erro': 'Campos obrigatórios: email e senha'}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({'erro': 'Email já cadastrado'}), 400

    novo_usuario = Usuario(email=email, nome=nome)
    novo_usuario.senha = senha  # usa o setter para gerar o hash

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário cadastrado com sucesso!'}), 201

# Login
@usuarios_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json() or {}
    usuario = Usuario.query.filter_by(email=dados.get('email')).first()

    if not usuario or not usuario.verificar_senha(dados.get('senha')):
        return jsonify({'erro': 'Credenciais inválidas'}), 401

    is_admin = usuario.email == "ofertasdoparceiroorlando@gmail.com"
    token = create_access_token(
        identity=str(usuario.id),
        additional_claims={"admin": is_admin}
    )

    return jsonify({'token': token}), 200

# Perfil
@usuarios_bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404

    return jsonify({
        'id': usuario.id,
        'nome': usuario.nome,
        'email': usuario.email
    }), 200

# Favoritos - listar
@usuarios_bp.route('/favoritos', methods=['GET'])
@jwt_required()
def listar_favoritos():
    usuario_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    favoritos_paginados = Favorito.query.filter_by(usuario_id=usuario_id)\
        .order_by(Favorito.data_favorito.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    resultado = []
    for favorito in favoritos_paginados.items:
        oferta = favorito.oferta
        if not oferta:
            continue
        resultado.append({
            'id': oferta.id,
            'titulo': oferta.titulo,
            'imagem': oferta.imagem,
            'loja': oferta.loja,
            'link_afiliado': oferta.link_afiliado,
            'link': oferta.link,
            'preco': oferta.preco,
            'favorito_id': favorito.id,
            'data_favorito': favorito.data_favorito.strftime('%d/%m/%Y %H:%M:%S')
        })

    return jsonify({
        'pagina': favoritos_paginados.page,
        'total_paginas': favoritos_paginados.pages,
        'total_favoritos': favoritos_paginados.total,
        'favoritos': resultado
    }), 200

# Favoritar
@usuarios_bp.route('/favoritos/<int:oferta_id>', methods=['POST'])
@jwt_required()
def favoritar(oferta_id):
    usuario_id = get_jwt_identity()

    favorito_existente = Favorito.query.filter_by(usuario_id=usuario_id, oferta_id=oferta_id).first()
    if favorito_existente:
        return jsonify({'mensagem': 'Oferta já favoritada.'}), 400

    novo_favorito = Favorito(usuario_id=usuario_id, oferta_id=oferta_id)
    db.session.add(novo_favorito)

    oferta = Oferta.query.get(oferta_id)
    if oferta:
        oferta.likes += 1
        comentarios = Comentario.query.filter_by(oferta_id=oferta.id).count()
        if oferta.likes >= 10 and comentarios >= 5 and not oferta.destaque:
            oferta.destaque = True

    db.session.commit()
    return jsonify({'mensagem': 'Oferta favoritada com sucesso!'}), 201

# Desfavoritar
@usuarios_bp.route('/favoritos/<int:oferta_id>', methods=['DELETE'])
@jwt_required()
def desfavoritar(oferta_id):
    usuario_id = get_jwt_identity()
    favorito = Favorito.query.filter_by(usuario_id=usuario_id, oferta_id=oferta_id).first()
    if not favorito:
        return jsonify({'mensagem': 'Favorito não encontrado.'}), 404

    db.session.delete(favorito)

    oferta = Oferta.query.get(oferta_id)
    if oferta and oferta.likes > 0:
        oferta.likes -= 1

    db.session.commit()
    return jsonify({'mensagem': 'Oferta desfavoritada com sucesso!'}), 200

# Estatísticas
@usuarios_bp.route('/estatisticas', methods=['GET'])
@jwt_required()
def estatisticas():
    total_usuarios = Usuario.query.count()
    total_ofertas = Oferta.query.count()
    total_favoritos = Favorito.query.count()

    ofertas_destaque = Oferta.query.filter_by(destaque=True).all()
    ofertas_mais_curtidas = Oferta.query.order_by(Oferta.likes.desc()).limit(5).all()

    destaque_serializado = [{
        'id': o.id,
        'titulo': o.titulo,
        'likes': o.likes,
        'destaque': o.destaque
    } for o in ofertas_destaque]

    mais_curtidas_serializado = [{
        'id': o.id,
        'titulo': o.titulo,
        'likes': o.likes
    } for o in ofertas_mais_curtidas]

    return jsonify({
        'total_usuarios': total_usuarios,
        'total_ofertas': total_ofertas,
        'total_favoritos': total_favoritos,
        'ofertas_destaque': destaque_serializado,
        'ofertas_mais_curtidas': mais_curtidas_serializado
    }), 200

# Meus favoritos
@usuarios_bp.route('/meus-favoritos', methods=['GET'])
@jwt_required()
def meus_favoritos():
    usuario_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    favoritos_paginados = Favorito.query.filter_by(usuario_id=usuario_id)\
        .order_by(Favorito.data_favorito.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    resultado = []
    for favorito in favoritos_paginados.items:
        oferta = favorito.oferta
        if not oferta:
            continue
        resultado.append({
            'id': oferta.id,
            'titulo': oferta.titulo,
            'imagem': oferta.imagem,
            'loja': oferta.loja,
            'link_afiliado': oferta.link_afiliado,
            'link': oferta.link,
            'preco': oferta.preco,
            'favorito_id': favorito.id,
            'data_favorito': favorito.data_favorito.strftime('%d/%m/%Y %H:%M:%S')
        })

    return jsonify({
        'pagina': favoritos_paginados.page,
        'total_paginas': favoritos_paginados.pages,
        'total_favoritos': favoritos_paginados.total,
        'favoritos': resultado
    }), 200

# Ofertas filtradas
@usuarios_bp.route('/ofertas-filtradas', methods=['GET'])
@jwt_required()
def ofertas_filtradas():
    loja = request.args.get('loja')
    categoria_id = request.args.get('categoria_id', type=int)
    data_min = request.args.get('data_min')
    data_max = request.args.get('data_max')

    query = Oferta.query

    if loja:
        query = query.filter(Oferta.loja.ilike(f'%{loja}%'))
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    if data_min:
        try:
            data_min = datetime.strptime(data_min, "%Y-%m-%d")
            query = query.filter(Oferta.data_criacao >= data_min)
        except ValueError:
            return jsonify({'erro': 'Formato inválido para data_min. Use YYYY-MM-DD'}), 400
    if data_max:
        try:
            data_max = datetime.strptime(data_max, "%Y-%m-%d")
            query = query.filter(Oferta.data_criacao <= data_max)
        except ValueError:
            return jsonify({'erro': 'Formato inválido para data_max. Use YYYY-MM-DD'}), 400

    ofertas = query.order_by(desc(Oferta.likes)).limit(20)

@usuarios_bp.route('/relatorio-favoritos', methods=['GET'])
@jwt_required()
def relatorio_favoritos():
    usuario_id = get_jwt_identity()
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    try:
        data_inicio = datetime.strptime(inicio, "%Y-%m-%d")
        data_fim = datetime.strptime(fim, "%Y-%m-%d")
    except:
        return jsonify({"erro": "Formato de data inválido. Use YYYY-MM-DD"}), 400

    favoritos = Favorito.query.filter(
        Favorito.usuario_id == usuario_id,
        Favorito.data_favorito >= data_inicio,
        Favorito.data_favorito <= data_fim
    ).all()

    resultado = []
    for fav in favoritos:
        oferta = Oferta.query.get(fav.oferta_id)
        resultado.append({
            "id": oferta.id,
            "titulo": oferta.titulo,
            "loja": oferta.loja,
            "preco": oferta.preco,
            "data_favorito": fav.data_favorito.strftime("%d/%m/%Y %H:%M:%S")
        })

    return jsonify(resultado), 200

@usuarios_bp.route('/verificar-alertas', methods=['GET'])
@jwt_required()
def verificar_alertas():
    usuario_id = get_jwt_identity()

    # Aqui você pode chamar uma função que verifica alertas por categoria, preço, etc.
    # Exemplo fictício:
    status = verificar_alerta_categoria(usuario_id)

    return jsonify({"status": status}), 200

@usuarios_bp.route('/exportar-favoritos', methods=['GET'])
@jwt_required()
def exportar_favoritos_csv():
    usuario_id = get_jwt_identity()
    favoritos = Favorito.query.filter_by(usuario_id=usuario_id).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Título', 'Loja', 'Preço', 'Data Favorito'])

    for fav in favoritos:
        oferta = Oferta.query.get(fav.oferta_id)
        writer.writerow([
            oferta.id,
            oferta.titulo,
            oferta.loja,
            f"R$ {oferta.preco:.2f}",
            fav.data_favorito.strftime("%d/%m/%Y %H:%M:%S")
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=favoritos.csv"}
    )
@usuarios_bp.route('/grafico-categorias', methods=['GET'])
@jwt_required()
def grafico_categorias():
    usuario_id = get_jwt_identity()

    # Exemplo: contar favoritos por categoria
    categorias = {}
    favoritos = Favorito.query.filter_by(usuario_id=usuario_id).all()

    for fav in favoritos:
        oferta = Oferta.query.get(fav.oferta_id)
        categoria = oferta.categoria or "Sem categoria"
        categorias[categoria] = categorias.get(categoria, 0) + 1

    return jsonify(categorias), 200

    