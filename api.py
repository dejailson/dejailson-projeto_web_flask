#!/usr/bin/python
import sqlite3
from flask import Flask, request
from flask_cors import CORS
from waitress import serve
from flasgger import Swagger
from werkzeug.wrappers import Response
from werkzeug.exceptions import BadRequest,MethodNotAllowed,InternalServerError,NotFound
import json
import os


def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn


def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''DROP TABLE users''')
        conn.execute('''
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY NOT NULL,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                telefone TEXT NOT NULL,
                endereco TEXT NOT NULL,
                cidade TEXT NOT NULL
            );
        ''')

        conn.commit()
        print("User table created successfully")
    except:
        print("User table creation failed - Maybe table")
    finally:
        conn.close()


def insert_user(user):
    inserted_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (nome, email, telefone, endereco, cidade) VALUES (?, ?, ?, ?, ?)", (user['nome'], user['email'], user['telefone'], user['endereco'], user['cidade']) )
        conn.commit()
        inserted_user = get_user_by_id(cur.lastrowid)
    except KeyError:
        conn.rollback()
        raise KeyError('Missing key in user')
    except:
        conn().rollback()

    finally:
        conn.close()

    return inserted_user


def get_users():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()

        # convert row objects to dictionary
        for i in rows:
            user = {}
            user["user_id"] = i["user_id"]
            user["nome"] = i["nome"]
            user["email"] = i["email"]
            user["telefone"] = i["telefone"]
            user["endereco"] = i["endereco"]
            user["cidade"] = i["cidade"]
            users.append(user)

    except:
        users = []

    return users


def get_user_by_id(user_id):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()

        # convert row object to dictionary
        user["user_id"] = row["user_id"]
        user["nome"] = row["nome"]
        user["email"] = row["email"]
        user["telefone"] = row["telefone"]
        user["endereco"] = row["endereco"]
        user["cidade"] = row["cidade"]
    except:
        user = {}

    return user


def update_user(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET nome = ?, email = ?, telefone = ?, endereco = ?, cidade = ? WHERE user_id =?", (user["nome"], user["email"], user["telefone"], user["endereco"], user["cidade"], user["user_id"],))
        conn.commit()
        #return the user
        updated_user = get_user_by_id(user["user_id"])
    except KeyError:
        conn.rollback()
        raise KeyError('Missing key in user')
    except:
        conn.rollback()
        updated_user = {}
    finally:
        conn.close()

    return updated_user


def delete_user(user_id):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE from users WHERE user_id = ?", (user_id,))
        conn.commit()
        message["status"] = "User deleted successfully"
    except:
        conn.rollback()
        message["status"] = "Cannot delete user"
    finally:
        conn.close()

    return message


users = []
user0 = {
    "nome": "Charles Effiong",
    "email": "charles@gamil.com",
    "telefone": "067765665656",
    "endereco": "Lui Str, Innsbruck",
    "cidade": "Austria"
}

user1 = {
    "nome": "Sam Adebanjo",
    "email": "samadebanjo@gamil.com",
    "telefone": "098765465",
    "endereco": "Sam Str, Vienna",
    "cidade": "Austria"
}

user2 = {
    "nome": "John Doe",
    "email": "johndoe@gamil.com",
    "telefone": "067765665656",
    "endereco": "John Str, Linz",
    "cidade": "Austria"
}

user3 = {
    "nome": "Mary James",
    "email": "maryjames@gamil.com",
    "telefone": "09878766676",
    "endereco": "AYZ Str, New york",
    "cidade": "United states"
}

users.append(user0)
users.append(user1)
users.append(user2)
users.append(user3)

create_db_table()

for i in users:
    print(insert_user(i))


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

template = {
  "swagger": "2.0",
  "info": {
    "title": "API do projeto Backend da disciplina desenvolvimento de sistemas web.",
    "description": "API do serviço de cadastro de usuários.",
  },
  "host": "127.0.0.1:5000",  # overrides localhost:500
  "basePath": "/api"  # base bash for blueprint registration
  #"operationId": "getmyData"
}

app.config['SWAGGER'] = {
    'title': 'API do projeto Backend da disciplina desenvolvimento de sistemas web.',
    'uiversion': 3,
    "specs_route": "/api/docs/",
    "doc_dir": "./docs/"  
}

swagger = Swagger(app, template= template)

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return Response(status=400, response=json.dumps({'messagem':'Requisição do cliente inválida.'}))

@app.errorhandler(MethodNotAllowed)
def handle_method_not_allowed(e):
    return Response(status=405, response=json.dumps({'messagem':'Método não permitido pelo servidor.'}))

@app.errorhandler(NotFound)
def handle_method_not_found(e):
    return Response(status=404, response=json.dumps({'messagem':'URI solicitada não foi encontrada.'}))

@app.errorhandler(InternalServerError)
def handle_internal_server_error(e):
    return Response(status=500, response=json.dumps({'messagem':'Erro interno no servidor aconteceu, retorne alguns minutos depois.'}))

app.register_error_handler(400, handle_bad_request)
app.register_error_handler(405, handle_method_not_allowed)
app.register_error_handler(404, handle_method_not_found)
app.register_error_handler(500, handle_internal_server_error)

@app.route('/api/users', methods=['GET'])
def api_get_users():
    """Listar todos os usuários
    ---
    tags:
        - Usuários
    responses:
        200:
            description: Lista de usuários
            schema:
                type: array
                items:
                    $ref: '#/definitions/UsuarioResponse'
                example:
                    - user_id: 1
                      nome: Charles Effiong
                      telefone: 067765665656
                      email: charles.effiong@gmail.com
                      cidade: Innsbruck
                      endereco: Lui Str
                    - user_id: 2
                      nome: Sam Adebanjo
                      email: samadebanjo@hotmail.com
                      telefone: 098765465
                      cidade: Vienna
                      endereco: Sam Str
        404: 
            description: URI Não foi encontrado
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'URI solicitada não foi encontrada.'}
        405: 
            description: Método não permitido pelo servidor
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Método não permitido pelo servidor.'}
        500:
            description: Erro interno no servidor.
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Erro interno no servidor aconteceu, retorne alguns minutos depois.' }    
            
    definitions:
        UsuarioResponse:
            type: object
            properties:
                user_id:
                    type: integer
                nome:
                    type: string
                email:
                    type: string
                telefone:  
                    type: string
                cidade:
                    type: string
            example:
                user_id: 1
                nome: Charles Effiong
                telefone: 067765665656
                email: charles.effiong@gmail.com
                cidade: Innsbruck
                endereco: Lui Str
    
    """
    return Response(status=200, response=json.dumps(get_users()))

@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    """Pesquisar usuário pelo seu user_id
    ---
    tags:
        - Usuários
    parameters:
        - in: path
          name: user_id
          required: true
          type: integer
          description: ID do usuário
    responses:
        200:
            description: Usuário encontrado
            schema:
                type: object
                $ref: '#/definitions/UsuarioResponse'

        404: 
            description: Usúario não encontrado
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Não foi encontrado usuário com o ID 100'}
        405: 
            description: Método não permitido pelo servidor
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Método não permitido pelo servidor.'}
        500:
            description: Erro interno no servidor.
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Erro interno no servidor aconteceu, retorne alguns minutos depois.' }

    """
    user = get_user_by_id(user_id)
    if (len(user.keys())==0):
        return Response(status=404, response=json.dumps({'messagem':f'Não foi encontrado usuário com o ID {user_id}'}))
    return Response(status=200, response=json.dumps(user))

@app.route('/api/users',  methods = ['POST'])
def api_add_user():
    """Salvar um usuário
    ---
    tags:
        - Usuários
    parameters:
        - in: body
          required: true
          name: Usuario
          schema:
            $ref: '#/definitions/Usuario'

    responses:
        201:
            description: Usuário cadastrado
            schema:
                type: object
                $ref: '#/definitions/UsuarioResponse'
        400: 
            description: Requisição do cliente inválida
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Requisição do cliente inválida.'}
        404: 
            description: URI Não foi encontrado
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'URI solicitada não foi encontrada.'}
        405: 
            description: Método não permitido pelo servidor
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Método não permitido pelo servidor.'}
        422:
            description: Erro ao cadastrar usuário
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Não foi possível processar o objeto enviado' }
        500:
            description: Erro interno no servidor.
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Erro interno no servidor aconteceu, retorne alguns minutos depois.' }
      
    definitions:
        Usuario:
            type: object
            properties:
                nome:
                    type: string
                email:
                    type: string
                telefone:  
                    type: string
                cidade:
                    type: string
                endereco:
                    type: string
            example:
                nome: Charles Effiong
                email: charles.effiong@gmail.com
                telefone: 067765665656
                cidade: Innsbruck
                endereco: Lui Str
        erro:
            type: object
            properties:
                messagem:
                    type: string
            
    
    """
    try:
        user = insert_user(request.get_json())
        return Response(status=201, response=json.dumps(user))
    except KeyError as e:
        return Response(status=422, response=json.dumps({'messagem':'Não foi possível processar o objeto enviado'}))

@app.route('/api/users/<user_id>',  methods = ['PUT'])
def api_update_user(user_id):
    """Atualizar um usuário pelo seu user_id
    ---
    tags:
        - Usuários
    parameters:
        - in: path
          name: user_id
          required: true
          type: integer
          description: ID do usuário
        - in: body
          required: true
          name: Usuario
          schema:
            $ref: '#/definitions/Usuario'

    responses:
        200:
            description: Usuário cadastrado
            schema:
                type: object
                $ref: '#/definitions/UsuarioResponse'
        400: 
            description: Requisição do cliente inválida
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Requisição do cliente inválida.'}
        404: 
            description: Usúario não encontrado
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Não foi encontrado usuário com o ID 100'}
        405: 
            description: Método não permitido pelo servidor
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Método não permitido pelo servidor.'}
        422:
            description: Erro ao cadastrar usuário
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Não foi possível processar o objeto enviado' }
        500:
            description: Erro interno no servidor.
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Erro interno no servidor aconteceu, retorne alguns minutos depois.' }
        
    """
    user_request = request.get_json()
    user_request['user_id'] = user_id
    
    try:
        user = update_user(user_request)
        if (len(user.keys())==0):
            return Response(status=404, response=json.dumps({'messagem':f'Não foi encontrado usuário com o ID {user_id}'}))
        return Response(status=200, response=json.dumps(user))
    except KeyError as e:
        return Response(status=422, response=json.dumps({'messagem':f'Não foi possível processar o objeto enviado'}))


@app.route('/api/users/<user_id>',  methods = ['DELETE'])
def api_delete_user(user_id):
    """Excluir usuário pelo seu user_id
    ---
    tags:
        - Usuários
    parameters:
        - in: path
          name: user_id
          required: true
          type: integer
          description: ID do usuário
    responses:
        204:
            description: Usuário excluído
        404: 
            description: Usúario não encontrado
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Não foi encontrado usuário com o ID 100'}
        405: 
            description: Método não permitido pelo servidor
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Método não permitido pelo servidor.'}
        500:
            description: Erro interno no servidor.
            schema:
                type: object
                $ref: '#/definitions/erro'
            examples:
                application/json: { 'messagem':'Erro interno no servidor aconteceu, retorne alguns minutos depois.' }
    
    """
    user = get_user_by_id(user_id)
    if (len(user.keys())==0):
        return Response(status=404, response=json.dumps({'messagem':f'Não foi encontrado usuário com o ID {user_id}'}))
    
    delete_user(user_id)
    
    return Response(status=204)

if __name__ == "__main__":
    port = os.environ.get('PORT')
    serve(app, host='0.0.0.0', port=port)