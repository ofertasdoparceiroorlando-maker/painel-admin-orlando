def verificar_alerta_categoria():
    LIMITE_FAVORITOS = 50

    categorias = [
        {'nome': 'Eletrônicos', 'favoritos': 42},
        {'nome': 'Moda', 'favoritos': 55},
        {'nome': 'Casa', 'favoritos': 30},
        {'nome': 'Beleza', 'favoritos': 61},
        {'nome': 'Esportes', 'favoritos': 61},
    ]

    for categoria in categorias:
        if categoria['favoritos'] > LIMITE_FAVORITOS:
            print(f"⚠️ Alerta: Categoria {categoria['nome']} ultrapassou {LIMITE_FAVORITOS} favoritos!")

def verificar_alerta_categoria(usuario_id):
    # Lógica de verificação de alertas vai aqui
    return "Alertas verificados"

def verificar_alerta_categoria(usuario_id):
    # Aqui você pode colocar a lógica real de verificação de alertas
    return "Alertas verificados"

