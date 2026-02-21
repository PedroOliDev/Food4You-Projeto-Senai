from flask import Blueprint, request, jsonify, session
from database import conectar
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from mysql.connector import Error
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    dados = request.get_json()
    nome = dados.get('name')
    email = dados.get('email')
    senha = dados.get('password')

    if not email or not senha or not nome:
        return jsonify({'message': 'Preencha todas as tabelas'}), 400

    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('INSERT INTO usuarios (nome, email, senha, foto_url) VALUES (%s, %s, %s, NULL)', (nome, email, senha))
        conn.commit()
        usuario_id = cursor.lastrowid  
        
        session['usuario_id'] = usuario_id
        session['usuario_nome'] = nome
        session['usuario_email'] = email

        return jsonify({'message': 'Usuário cadastrado com sucesso!', 'usuario': {'id': usuario_id, 'nome': nome, 'email': email, 'foto_url': None}}), 201
    except Error as e:
        if e.errno == 1062:
            return jsonify({'message': 'Usuário já existe, vá para página de entrada.'}), 409
        return jsonify({'message': f'Erro no servidor: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('password')
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuarios WHERE email = %s AND senha = %s', (email, senha))
        usuario = cursor.fetchone()
        if usuario:
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            session['usuario_email'] = usuario['email']
            session['is_admin'] = usuario['is_admin'] == 1  
            return jsonify({'message': 'Login bem-sucedido!', 'usuario': usuario}), 200
        else:
            return jsonify({'message': 'Email ou senha inválidos'}), 401
    except Error as e:
        return jsonify({'message': 'Erro no servidor'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@auth_bp.route('/register-google', methods=['POST'])
def register_google():
    dados = request.get_json()
    token = dados.get('token')
    if not token:
        return jsonify({'message': 'Token não fornecido'}), 400
    try:
        idinfo = id_token.verify_oauth2_token(token, grequests.Request(), "844429812632-gi775pp6vfiqo2kbj5h0h9bam1u90pon.apps.googleusercontent.com")
        email = idinfo.get('email')
        nome = idinfo.get('name')
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
        usuario = cursor.fetchone()
        if usuario:
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            session['usuario_email'] = usuario['email']
            session['is_admin'] = usuario['is_admin'] == 1  
            return jsonify({'message': 'Login com Google feito com sucesso!', 'usuario': usuario}), 200
        else:
            cursor.execute('INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)', (nome, email, 'GOOGLE'))
            conn.commit()
            usuario_id = cursor.lastrowid
            usuario = {'id': usuario_id, 'nome': nome, 'email': email, 'foto_url': None, 'is_admin': 0}
            session['usuario_id'], session['usuario_nome'], session['usuario_email'], session['is_admin'] = usuario_id, nome, email, False
            return jsonify({'message': 'Usuário Google cadastrado!', 'usuario': usuario}), 201
    except Exception as e:
        return jsonify({'message': 'Token inválido'}), 401
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close(); conn.close()

@auth_bp.route('/perfil', methods=['GET'])
def perfil():
    if 'usuario_id' not in session:
        return jsonify({'message': 'Não autenticado'}), 401
    try:
        conn = conectar(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nome, email, foto_url FROM usuarios WHERE id = %s", (session['usuario_id'],))
        usuario = cursor.fetchone()
        return jsonify(usuario), 200 if usuario else 404
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

@auth_bp.route('/atualizar-perfil', methods=['POST'])
def atualizar_perfil():
    if 'usuario_id' not in session: return jsonify({'message': 'Não autenticado'}), 401
    usuario_id = session['usuario_id']
    nome = request.form.get('nome'); senha = request.form.get('senha'); foto = request.files.get('foto')
    foto_url = None
    if foto:
        pasta_fotos = os.path.join('static', 'fotos')
        if not os.path.exists(pasta_fotos): os.makedirs(pasta_fotos)
        extensao = os.path.splitext(foto.filename)[1]
        caminho_foto = os.path.join(pasta_fotos, f'{usuario_id}{extensao}')
        foto.save(caminho_foto)
        foto_url = f'/static/fotos/{usuario_id}{extensao}'
    try:
        conn = conectar(); cursor = conn.cursor()
        query = "UPDATE usuarios SET nome=%s, senha=%s" + (", foto_url=%s" if foto_url else "") + " WHERE id=%s"
        valores = [nome, senha, foto_url, usuario_id] if foto_url else [nome, senha, usuario_id]
        cursor.execute(query, valores); conn.commit()
        session['usuario_nome'] = nome
        return jsonify({'message': 'Perfil atualizado', 'foto_url': foto_url}), 200
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso'}), 200