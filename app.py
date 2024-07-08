from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flasgger import Swagger
import json
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'

# Configura o logger para o SQLAlchemy
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

db = SQLAlchemy(app)
swagger = Swagger(app)

@app.before_first_request
def cria_banco():
    db.create_all()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

class Cliente(db.Model):
    __tablename__ = 'cliente'

    id_cliente = db.Column(db.Integer, primary_key= True)
    cliente_nome = db.Column(db.String(50), nullable = False)
    cliente_telefone = db.Column(db.String(20), nullable = False)
    cliente_email = db.Column(db.String(50), nullable = False)
    cliente_cpf = db.Column(db.String(100), nullable = False, unique = True)
    pedido = db.relationship('Pedido', backref='cliente', lazy=True)


    def to_json(self):
        return {
            'id_cliente': self.id_cliente,
            'cliente_nome': self.cliente_nome,
            'cliente_telefone': self.cliente_telefone,
            'cliente_email': self.cliente_email,
            'cliente_cpf': self.cliente_cpf,
            'pedidos': [pedido.to_json() for pedido in self.pedido]
        }

class Pedido(db.Model):
    __tablename__ = 'pedido'

    id_pedido = db.Column(db.Integer, primary_key= True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'))
    pedido_data = db.Column(db.Date, nullable=False)
    pedido_dataPagamento = db.Column(db.Date, nullable=False)
    pedido_status = db.Column(db.String(10), nullable=False)
    produtoPedido = db.relationship('ProdutoPedido', backref='pedido', lazy=True)
    pedido_preco = db.Column(db.Float(precision=2), nullable=False)

    def to_json(self):
        return {
            'id_pedido': self.id_pedido,
            'id_cliente': self.id_cliente,
            'pedido_data': self.pedido_data.isoformat() if self.pedido_data else None,
            'pedido_dataPagamento': self.pedido_dataPagamento.isoformat() if self.pedido_dataPagamento else None,
            'pedido_status': self.pedido_status,
            'pedido_produtosPedido': [produtoPedido.to_json() for produtoPedido in self.produtoPedido],
            'pedido_preco': self.pedido_preco,
        }

class ProdutoPedido(db.Model):
    __tablename__ = 'produtoPedido'

    id_pedido = db.Column(db.Integer, db.ForeignKey('pedido.id_pedido'))
    id_produtoPedido = db.Column(db.Integer, primary_key=True)
    produto_quantidade = db.Column(db.Integer, nullable=False)
    produto_sku = db.Column(db.String, db.ForeignKey('produto.produto_sku'))

    def to_json(self):
        return {
            'id_pedido': self.id_pedido,
            'id_produtoPedido': self.id_produtoPedido,
            'produto_quantidade': self.produto_quantidade,
            'produto_sku': self.produto_sku
        }

class Produto(db.Model):
    __tablename__ = 'produto'

    produto_sku = db.Column(db.String(32), nullable = False, primary_key = True)
    produto_nome = db.Column(db.String(50), nullable = False)
    produto_estoque = db.Column(db.Integer, nullable = False)
    produto_preco = db.Column(db.Float(precision=2), nullable=False)

    def to_json(self):
        return {
            'produto_sku': self.produto_sku,
            'produto_nome': self.produto_nome,
            'produto_estoque': self.produto_estoque,
            'produto_preco': self.produto_preco
        }

class ProdutoReposicao(db.Model):
    __tablename__ = 'produtoReposicao'

    id_pedido = db.Column(db.Integer, db.ForeignKey('pedido.id_pedido'))
    id_reposicao = db.Column(db.Integer, nullable=False, primary_key=True)
    produto_quantidade = db.Column(db.Integer, nullable=False)
    produto_sku = db.Column(db.String, db.ForeignKey('produto.produto_sku'))

    def to_json(self):
        return {
            'id_pedido': self.id_pedido,
            'id_reposicao': self.id_reposicao,
            'produto_quantidade': self.produto_quantidade,
            'produto_sku': self.produto_sku
        }
    
class Carga(db.Model):
    __tablename__ = 'carga'

    id_carga = db.Column(db.Integer, nullable=False, primary_key = True)
    cliente_cpf = db.Column(db.String(100), nullable = False)
    cliente_nome = db.Column(db.String(50), nullable = False)
    cliente_telefone = db.Column(db.String(20), nullable = False)
    cliente_email = db.Column(db.String(50), nullable = False)
    pedido_data = db.Column(db.Date, nullable=False)
    pedido_dataPagamento = db.Column(db.Date, nullable=False)    
    produtoPedido_sku = db.Column(db.String(32), nullable = False)
    produtoPedido_nome = db.Column(db.String(50), nullable = False)
    produto_quantidade = db.Column(db.Integer, nullable=False)

    def to_json(self):
        return {
            'id_carga': self.id_carga,
            'cliente_cpf': self.cliente_cpf,
            'cliente_nome': self.cliente_nome,
            'cliente_telefone': self.cliente_telefone,
            'cliente_email': self.cliente_email,
            'pedido_data': self.pedido_data.isoformat() if self.pedido_data else None,
            'pedido_dataPagamento': self.pedido_dataPagamento.isoformat() if self.pedido_dataPagamento else None,
            'produtoPedido_sku': self.produtoPedido_sku,
            'produtoPedido_nome': self.produtoPedido_nome,
            'produto_quantidade': self.produto_quantidade
        }

# Criar uma carga
@app.route("/carga", methods=["POST"])
def cria_carga():
    """
    Cria uma nova carga no sistema.

    ---
    tags:
      - Carga
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            cliente_cpf:
              type: string
              description: CPF do cliente.
            cliente_nome:
              type: string
              description: Nome do cliente.
            cliente_telefone:
              type: string
              description: Telefone do cliente.
            cliente_email:
              type: string
              description: Email do cliente.
            pedido_data:
              type: string
              format: date
              description: Data do pedido (formato YYYY-MM-DD).
            pedido_dataPagamento:
              type: string
              format: date
              description: Data de pagamento do pedido (formato YYYY-MM-DD).
            produtoPedido_sku:
              type: string
              description: SKU do produto do pedido.
            produtoPedido_nome:
              type: string
              description: Nome do produto do pedido.
            produto_quantidade:
              type: integer
              description: Quantidade do produto do pedido.
    responses:
      201:
        description: Carga criada com sucesso.
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: integer
                  example: 201
                message:
                  type: string
                  example: Carga criada com sucesso.
                data:
                  type: object
                  example:
                    cliente_cpf: "123.456.789-00"
                    cliente_nome: "Fulano de Tal"
                    cliente_telefone: "(11) 99999-9999"
                    cliente_email: "fulano@example.com"
                    pedido_data: "2024-07-01"
                    pedido_dataPagamento: "2024-07-02"
                    produtoPedido_sku: "SKU123"
                    produtoPedido_nome: "Produto ABC"
                    produto_quantidade: 10
      400:
        description: Erro ao criar carga.
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: integer
                  example: 400
                message:
                  type: string
                  example: Erro ao criar carga.
                data:
                  type: object
                  example: {}

    """
    body = request.get_json()

    try:
        clienteX = Cliente.query.filter_by(cliente_cpf=body["cliente_cpf"]).first()
        if clienteX is not None: #Caso JÁ EXISTA o cliente no banco
          produtoProcuradoX = Produto.query.filter_by(produto_sku = body["produtoPedido_sku"]).first()
          if produtoProcuradoX.produto_estoque >= body["produto_quantidade"]: #Caso a quantidade no estoque for menor que a necessária pro pedido
            pedidoX = Pedido(
              id_cliente = clienteX.id_cliente,
              pedido_data = datetime.strptime(body["pedido_data"], "%Y-%m-%d").date(),
              pedido_dataPagamento = datetime.strptime(body["pedido_dataPagamento"], "%Y-%m-%d").date(),
              pedido_status = 'Pronto para envio',
              pedido_preco = body["produto_quantidade"] * produtoProcuradoX.produto_preco
            )
            db.session.add(pedidoX)
            db.session.commit()  # Commit para garantir que o pedido tenha um ID
            produtoPedidoX = ProdutoPedido(
              id_pedido = pedidoX.id_pedido,  # Associar o produto pedido ao pedido criado
              produto_quantidade = body["produto_quantidade"],
              produto_sku = body["produtoPedido_sku"]
            )
            db.session.add(produtoPedidoX)
            produtoProcuradoX.produto_estoque -= body["produto_quantidade"]
            db.session.commit()
          else:
            pedidoX = Pedido(
              id_cliente = clienteX.id_cliente,
              pedido_data = datetime.strptime(body["pedido_data"], "%Y-%m-%d").date(),
              pedido_dataPagamento = datetime.strptime(body["pedido_dataPagamento"], "%Y-%m-%d").date(),
              pedido_status = 'Dependente de Reposição de Estoque',
              pedido_preco = body["produto_quantidade"] * produtoProcuradoX.produto_preco
            )
            db.session.add(pedidoX)
            db.session.commit()  # Commit para garantir que o pedido tenha um ID
            produtoPedidoX = ProdutoReposicao(
              id_pedido = pedidoX.id_pedido,  # Associar o produto pedido ao pedido criado
              produto_quantidade = body["produto_quantidade"],
              produto_sku = body["produtoPedido_sku"]
            )
            db.session.add(produtoPedidoX)
            db.session.commit()
        else: #caso NÃO exista o cliente no banco
          clienteX = Cliente(
            cliente_nome=body["cliente_nome"],
            cliente_telefone=body["cliente_telefone"],
            cliente_email=body["cliente_email"],
            cliente_cpf=body["cliente_cpf"],
          )
          db.session.add(clienteX)
          db.session.commit()  # Commit para garantir que o cliente tenha um ID
          produtoProcuradoX = Produto.query.filter_by(produto_sku = body["produtoPedido_sku"]).first()
          if produtoProcuradoX.produto_estoque >= body["produto_quantidade"]: #Caso a quantidade no estoque for menor que a necessária pro pedido
            pedidoX = Pedido(
              id_cliente = clienteX.id_cliente,
              pedido_data = datetime.strptime(body["pedido_data"], "%Y-%m-%d").date(),
              pedido_dataPagamento = datetime.strptime(body["pedido_dataPagamento"], "%Y-%m-%d").date(),
              pedido_status = 'Pronto para envio',
              pedido_preco = body["produto_quantidade"] * produtoProcuradoX.produto_preco
            )
            db.session.add(pedidoX)
            db.session.commit()  # Commit para garantir que o pedido tenha um ID
            produtoPedidoX = ProdutoPedido(
              id_pedido = pedidoX.id_pedido,  # Associar o produto pedido ao pedido criado
              produto_quantidade = body["produto_quantidade"],
              produto_sku = body["produtoPedido_sku"]
            )
            db.session.add(produtoPedidoX)
            produtoProcuradoX.produto_estoque -= body["produto_quantidade"]
            db.session.commit()
          else:
            pedidoX = Pedido(
              id_cliente = clienteX.id_cliente,
              pedido_data = datetime.strptime(body["pedido_data"], "%Y-%m-%d").date(),
              pedido_dataPagamento = datetime.strptime(body["pedido_dataPagamento"], "%Y-%m-%d").date(),
              pedido_status = 'Dependente de Reposição de Estoque',
              pedido_preco = body["produto_quantidade"] * produtoProcuradoX.produto_preco
            )
            db.session.add(pedidoX)
            db.session.commit()  # Commit para garantir que o pedido tenha um ID
            produtoPedidoX = ProdutoReposicao(
              id_pedido = pedidoX.id_pedido,  # Associar o produto pedido ao pedido criado
              produtoReposicao_quantidade = body["produto_quantidade"],
              produtoReposicao_sku = body["produtoPedido_sku"]
            )
            db.session.add(produtoPedidoX)
            db.session.commit()
        cargaX = Carga(
            cliente_cpf=body["cliente_cpf"],
            cliente_nome=body["cliente_nome"],
            cliente_telefone=body["cliente_telefone"],
            cliente_email=body["cliente_email"],
            pedido_data = datetime.strptime(body["pedido_data"], "%Y-%m-%d").date(),
            pedido_dataPagamento = datetime.strptime(body["pedido_dataPagamento"], "%Y-%m-%d").date(),
            produtoPedido_sku=body["produtoPedido_sku"],
            produtoPedido_nome=body["produtoPedido_nome"],
            produto_quantidade=body["produto_quantidade"],
        )
        db.session.add(cargaX)
        db.session.commit()
        return gera_response(201, "Carga", cargaX.to_json(), "Procedimento Realizado com Sucesso.")
    except Exception as e:
        print('Erro', e)
        return gera_response(400, "Error", {}, "Erro ao realizar procedimentos no sistema!")

# Visualizar todas as tabelas no formato JSON
@app.route("/allTables", methods=["GET"])
def todas_tabelas():
    """
    Obter dados de todas as tabelas

    ---
    tags:
      - Bazar Tem Tudo
    summary: Retorna dados de todas as tabelas
    description: Endpoint que retorna os dados de todas as tabelas do sistema Bazar Tem Tudo, incluindo clientes, pedidos, produtos em pedidos, produtos e produtos de reposição.
    responses:
      200:
        description: Dados de todas as tabelas retornados com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: Sucesso
                message:
                  type: string
                  example: Bazar Tem Tudo
                data:
                  type: object
                  properties:
                    clientes:
                      type: array
                      items:
                        type: object
                    pedidos:
                      type: array
                      items:
                        type: object
                    produtosPedido:
                      type: array
                      items:
                        type: object
                    produtos:
                      type: array
                      items:
                        type: object
                    produtosReposicao:
                      type: array
                      items:
                        type: object
    """
    todas_tabelas = {
        'clientes': [cliente.to_json() for cliente in Cliente.query.all()],
        'produtos': [carga.to_json() for carga in Produto.query.all()],
        'produtosReposicao': [carga.to_json() for carga in ProdutoReposicao.query.all()]
    }
    return gera_response(200, "Bazar Tem Tudo", todas_tabelas, "Sucesso")

# Criar um cliente
@app.route("/cliente", methods=["POST"])
def cria_cliente():
    """
Cria um novo cliente no sistema.

---
tags:
  - Cliente
parameters:
  - in: body
    name: body
    required: true
    schema:
      type: object
      properties:
        cliente_nome:
          type: string
          description: Nome do cliente.
        cliente_telefone:
          type: string
          description: Número de telefone do cliente.
        cliente_email:
          type: string
          description: Endereço de e-mail do cliente.
        cliente_cpf:
          type: string
          description: CPF do cliente.
responses:
  201:
    description: Cliente criado com sucesso.
    content:
      application/json:
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 201
            message:
              type: string
              example: Cliente criado com sucesso.
            data:
              type: object
              example: {"id": 1, "cliente_nome": "Exemplo Cliente", "cliente_telefone": "(00) 0000-0000", "cliente_email": "cliente@example.com", "cliente_cpf": "000.000.000-00"}
  400:
    description: Erro ao realizar procedimentos no sistema.
    content:
      application/json:
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 400
            message:
              type: string
              example: Erro ao realizar procedimentos no sistema.
            data:
              type: object
              example: {}
"""
    body = request.get_json()

    try:
        clienteX = Cliente(
            cliente_nome=body["cliente_nome"],
            cliente_telefone=body["cliente_telefone"],
            cliente_email=body["cliente_email"],
            cliente_cpf=body["cliente_cpf"]
        )
        db.session.add(clienteX)
        db.session.commit()  # Commit para garantir que o cliente tenha um ID
        return gera_response(201, "Cliente", clienteX.to_json(), "Cliente criado com Sucesso.")  
    except Exception as e:
        print('Erro', e)
        return gera_response(400, "Error", {}, "Erro ao realizar procedimentos no sistema!")

# Criar um produto
@app.route("/produto", methods=["POST"])
def cria_produto():
    """
Cria um novo produto no sistema.

---
tags:
  - Produto
parameters:
  - in: body
    name: body
    required: true
    schema:
      type: object
      properties:
        produto_sku:
          type: string
          description: SKU do produto.
        produto_estoque:
          type: integer
          description: Quantidade em estoque do produto.
        produto_nome:
          type: string
          description: Nome do produto.
        produto_preco:
          type: number
          description: Preço do produto.
responses:
  201:
    description: Produto criado com sucesso.
    content:
      application/json:
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 201
            message:
              type: string
              example: Produto criado com sucesso.
            data:
              type: object
              example: {"id": 1, "produto_sku": "SKU123", "produto_estoque": 100, "produto_nome": "Exemplo Produto", "produto_preco": 99.99}
  400:
    description: Erro ao realizar procedimentos no sistema.
    content:
      application/json:
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 400
            message:
              type: string
              example: Erro ao realizar procedimentos no sistema.
            data:
              type: object
              example: {}
"""
    body = request.get_json()

    try:
        produtoX = Produto(
              produto_sku = body["produto_sku"],
              produto_estoque = body["produto_estoque"],
              produto_nome = body["produto_nome"],
              produto_preco = body["produto_preco"]
            )
        db.session.add(produtoX)
        db.session.commit()
        return gera_response(201, "Produto", produtoX.to_json(), "Produto criado com Sucesso.") 
     
    except Exception as e:
        print('Erro', e)
        return gera_response(400, "Error", {}, "Erro ao realizar procedimentos no sistema!")
    

def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_do_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")


app.run(debug=True)