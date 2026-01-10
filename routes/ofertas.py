from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from pydantic import ValidationError
from models import Oferta, Comentario, Usuario, Favorito
from schemas import ComentarioSchema
from services.alertas import verificar_alerta_categoria
from services.telegram import enviar_mensagem, enviar_foto

print(" Arquivo ofertas.py foi carregado")

ofertas_bp = Blueprint('ofertas_bp', __name__)

# 🔍 Listar todas as ofertas (com filtro opcional)
@ofertas_bp.route('/', methods=['GET'])
def listar_ofertas():
    categoria = request.args.get('categoria')
    query = Oferta.query
    if categoria:
        query = query.filter_by(categoria=categoria)
    ofertas = query.order_by(Oferta.data_criacao.desc()).all()

    resultado = [{
        'id': o.id,
        'titulo': o.titulo,
        'descricao': o.descricao,
        'preco': o.preco,
        'imagem': o.imagem,
        'link_afiliado': o.link_afiliado,
        'loja': o.loja,
        'categoria': o.categoria,
        'destaque': o.destaque,
        'likes': o.likes,
        'data_criacao': o.data_criacao.strftime('%d/%m/%Y %H:%M')
    } for o in ofertas]

    return jsonify(resultado)

# 🆕 Criar nova oferta (com envio ao Telegram)
@ofertas_bp.route('/cadastrar', methods=['POST'])
@jwt_required()
def cadastrar_oferta():
    claims = get_jwt()
    if not claims.get("admin"):
        return jsonify({"erro": "Acesso negado"}), 403

    dados = request.get_json()

    campos_obrigatorios = ['titulo', 'descricao', 'preco', 'imagem', 'link_afiliado', 'loja', 'categoria']
    for campo in campos_obrigatorios:
        if not dados.get(campo):
            return jsonify({'erro': f'O campo "{campo}" é obrigatório.'}), 400

    nova = Oferta(**{
        **dados,
        'destaque': dados.get('destaque', False),
        'likes': dados.get('likes', 0)
    })

    db.session.add(nova)
    db.session.commit()

    TEMPLATE_MENSAGEM = (
        "🔥 *Nova Oferta!*\n\n"
        "*{titulo}*\n"
        "💰 Preço: R$ {preco}\n"
        "🏬 Loja: {loja}\n"
        "📦 Categoria: {categoria}\n\n"
        "{descricao}\n\n"
        "[👉 Comprar agora]({link_afiliado})"
    )

    legenda = TEMPLATE_MENSAGEM.format(
        titulo=nova.titulo,
        preco=nova.preco,
        loja=nova.loja,
        categoria=nova.categoria,
        descricao=nova.descricao,
        link_afiliado=nova.link_afiliado
    )

    # ✅ Decide se envia texto ou foto
    if nova.imagem:
        enviar_foto(legenda, nova.imagem)
    else:
        enviar_mensagem(legenda)

    return jsonify({
        'mensagem': 'Oferta criada com sucesso e enviada ao Telegram!',
        'id': nova.id,
        'titulo': nova.titulo,
        'descricao': nova.descricao,
        'preco': nova.preco,
        'imagem': nova.imagem,
        'link_afiliado': nova.link_afiliado,
        'loja': nova.loja,
        'categoria': nova.categoria,
        'destaque': nova.destaque,
        'likes': nova.likes,
        'data_criacao': nova.data_criacao.strftime('%d/%m/%Y %H:%M')
    }), 201

# ✏️ Editar oferta
@ofertas_bp.route('/editar/<int:id>', methods=['PUT'])
@jwt_required()
def editar_oferta(id):
    claims = get_jwt()
    if not claims.get("admin"):
        return jsonify({"erro": "Acesso negado"}), 403

    dados = request.get_json()
    oferta = Oferta.query.get(id)

    if not oferta:
        return jsonify({"erro": "Oferta não encontrada"}), 404

    oferta.titulo = dados['titulo']
    oferta.descricao = dados['descricao']
    oferta.preco = dados['preco']
    oferta.link_afiliado = dados['link_afiliado']
    db.session.commit()

    return jsonify({"mensagem": "Oferta atualizada com sucesso!"}), 200

# ❌ Deletar oferta
@ofertas_bp.route('/deletar/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar_oferta(id):
    claims = get_jwt()
    if not claims.get("admin"):
        return jsonify({"erro": "Acesso negado"}), 403

    oferta = Oferta.query.get(id)
    if not oferta:
        return jsonify({"erro": "Oferta não encontrada"}), 404

    db.session.delete(oferta)
    db.session.commit()

    return jsonify({"mensagem": "Oferta deletada com sucesso!"}), 200

# ❤️ Curtir oferta
@ofertas_bp.route('/<int:id>/like', methods=['PATCH'])
def curtir_oferta(id):
    oferta = Oferta.query.get_or_404(id)
    oferta.likes += 1
    db.session.commit()
    return jsonify({'likes': oferta.likes})

# 💬 Listar comentários
@ofertas_bp.route('/<int:oferta_id>/comentarios', methods=['GET'])
def listar_comentarios(oferta_id):
    comentarios = Comentario.query.filter_by(oferta_id=oferta_id).order_by(Comentario.data_criacao.desc()).all()
    resultado = [{
        'id': c.id,
        'texto': c.texto,
        'autor': c.autor.nome,
        'data': c.data_criacao.strftime('%d/%m/%Y %H:%M')
    } for c in comentarios]
    return jsonify(resultado)

# 📝 Comentar oferta
@ofertas_bp.route('/<int:oferta_id>/comentarios', methods=['POST'])
@jwt_required()
def comentar_oferta(oferta_id):
    dados = request.get_json()
    try:
        comentario = ComentarioSchema(**dados)
    except ValidationError as e:
        return jsonify({"erro": "Validação falhou", "detalhes": e.errors()}), 422

    usuario_id = get_jwt_identity()
    novo = Comentario(
        texto=comentario.texto,
        autor_id=usuario_id,
        oferta_id=oferta_id,
        data_criacao=datetime.utcnow()
    )
    db.session.add(novo)
    db.session.commit()

    return jsonify({
        "mensagem": "Comentário salvo com sucesso!",
        "comentario": {
            "id": novo.id,
            "texto": novo.texto,
            "autor_id": novo.autor_id,
            "oferta_id": novo.oferta_id,
            "data_criacao": novo.data_criacao.strftime('%d/%m/%Y %H:%M')
        }
    }), 201

# ❤️ Favoritar oferta
@ofertas_bp.route('/favoritar/<int:id_oferta>', methods=["POST"])
@jwt_required()
def favoritar_oferta(id_oferta):
    usuario_id = get_jwt_identity()
    favorito = Favorito(usuario_id=usuario_id, oferta_id=id_oferta, data_favorito=datetime.utcnow())
    db.session.add(favorito)
    db.session.commit()
    return jsonify({'mensagem': 'Oferta favoritada com sucesso!'}), 201

# 🔔 Verificar alertas
@ofertas_bp.route('/verificar-alertas', methods=['GET'])
@jwt_required()
def verificar_alertas_route():
    verificar_alerta_categoria()
    return jsonify({'status': 'Alertas verificados'}), 200

# 📊 Categorias mais engajadas
@ofertas_bp.route('/categorias-mais-engajadas', methods=['GET'])
@jwt_required()
def categorias_mais_engajadas():
    categorias = [
        {'nome': 'Eletrônicos', 'favoritos': 42},
        {'nome': 'Moda', 'favoritos': 55},
        {'nome': 'Casa', 'favoritos': 30},
        {'nome': 'Beleza', 'favoritos': 61},
        {'nome': 'Esportes', 'favoritos': 61},
    ]
    categorias_ordenadas = sorted(categorias, key=lambda c: c['favoritos'], reverse=True)
    return jsonify(categorias_ordenadas), 200

# 🛠 Debug
@ofertas_bp.route('/listar-ofertas-debug', methods=['GET'])
def listar_ofertas_debug():
    ofertas = Oferta.query.all()
    resultado = [{'id': o.id, 'titulo': o.titulo, 'loja': o.loja, 'preco': o.preco} for o in ofertas]
    return jsonify(resultado), 200

# 📊 Painel HTML
@ofertas_bp.route('/painel', methods=['GET'])
def painel_ofertas():
    ofertas = Oferta.query.all()
    return render_template('painel.html', ofertas=ofertas)

# Exibir formulário HTML
@ofertas_bp.route('/nova-oferta', methods=['GET'])
def nova_oferta_form():
    return render_template('nova_oferta.html')

# Salvar dados do formulário
@ofertas_bp.route('/nova-oferta', methods=['POST'])
def salvar_nova_oferta():
    titulo = request.form.get('titulo')
    loja = request.form.get('loja')
    preco = request.form.get('preco')
    categoria = request.form.get('categoria')

    nova = Oferta(
        titulo=titulo,
        loja=loja,
        preco=float(preco),
        categoria=categoria
    )
    db.session.add(nova)
    db.session.commit()

    return redirect(url_for('ofertas_bp.painel_ofertas'))

# 🔍 Rota para listar todas as ofertas cadastradas
@ofertas_bp.route('/todas', methods=['GET'])
def todas_ofertas():
    ofertas = Oferta.query.all()
    resultado = [{
        "id": o.id,
        "titulo": o.titulo,
        "loja": o.loja,
        "preco": float(o.preco),
        "categoria": o.categoria
    } for o in ofertas]
    return jsonify(resultado)
