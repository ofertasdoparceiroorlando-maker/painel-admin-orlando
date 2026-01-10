# 🛒 OfertasdoOrlandoOliveira

Projeto backend em **Flask/Python** para gerenciamento de ofertas e produtos, com integração a um painel frontend moderno.

---

## 🚀 Funcionalidades

- Autenticação de usuários (login com token JWT)
- Cadastro, edição e exclusão de ofertas
- Gerenciamento de produtos e categorias
- Favoritos com persistência em LocalStorage
- Filtros avançados e busca global
- Exportação CSV de todas as ofertas ou apenas favoritos
- Dashboard interativo com gráficos (Chart.js)
- Interface frontend responsiva com modo escuro, toasts e botão de voltar ao topo

---

## 📂 Estrutura do projeto
OfertasdoOrlandoOliveira/
├── app.py               # Ponto de entrada principal
├── main.py              # Alternativa de inicialização
├── models.py            # Modelos de dados
├── extensions.py        # Configuração de extensões (db, jwt, etc.)
├── schemas.py           # Definições de schemas
├── test_db.py          # Scripts de teste do banco
├── routes/             # Rotas da API
│   ├── __init__.py
│   ├── admin.py
│   ├── auth.py
│   ├── ofertas.py
│   ├── produto.py
│   └── usuarios.py
├── services/           # Lógica de negócio
├── utils/              # Funções utilitárias
├── database/           # Configuração e scripts de banco
├── migrations/         # Migrações do banco (Flask-Migrate)
├── static/             # Arquivos estáticos (CSS, JS)
│   ├── style.css
│   └── painel.js
├── templates/          # Templates HTML (Jinja2)
│   └── painel.html
├── frontend/           # Pasta reservada para frontend adicional
├── instance/           # Configurações locais
├── .env                # Variáveis de ambiente
├── requirements.txt     # Dependências do projeto
├── README.md            # Documentação do projeto
└── venv/ ou .venv/     # Ambiente virtual

## ⚙️ Configuração

1. **Clonar o repositório**
   ```bash
   git clone https://github.com/ofertasdoparceiroorlando-maker/OfertasdoOrlandoOliveira.git
   cd OfertasdoOrlandoOliveira

## 📡 Endpoints da API

### 🔑 Autenticação
- `POST /usuarios/login`  
  Faz login do usuário e retorna um token JWT.

### 👤 Usuários
- `POST /usuarios`  
  Cria um novo usuário.  
- `GET /usuarios/{id}`  
  Retorna informações de um usuário específico.  
- `PUT /usuarios/{id}`  
  Atualiza dados de um usuário.  
- `DELETE /usuarios/{id}`  
  Remove um usuário.

### 🛍️ Ofertas
- `GET /ofertas/todas`  
  Lista todas as ofertas cadastradas.  
- `POST /ofertas`  
  Cadastra uma nova oferta.  
- `GET /ofertas/{id}`  
  Retorna detalhes de uma oferta específica.  
- `PUT /ofertas/{id}`  
  Atualiza uma oferta existente.  
- `DELETE /ofertas/{id}`  
  Exclui uma oferta.

### 📦 Produtos
- `GET /produto/todos`  
  Lista todos os produtos.  
- `POST /produto`  
  Cadastra um novo produto.  
- `GET /produto/{id}`  
  Retorna detalhes de um produto específico.  
- `PUT /produto/{id}`  
  Atualiza um produto existente.  
- `DELETE /produto/{id}`  
  Exclui um produto.

### ⚙️ Admin
- `GET /admin/dashboard`  
  Retorna estatísticas gerais do sistema.  
- `GET /admin/usuarios`  
  Lista todos os usuários cadastrados.  
