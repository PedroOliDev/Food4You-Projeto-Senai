from flask import Blueprint, app, logging, request, jsonify, session, render_template, redirect, url_for
from database import conectar
from mysql.connector import Error
import os, json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_page():
    if 'usuario_id' not in session or not session.get('is_admin', False):
        return redirect('/') 
    return render_template('admin.html') 

@admin_bp.route('/check_admin', methods=['GET'])
def check_admin():
    return jsonify({'is_admin': session.get('is_admin', False)}), 200

# --- Restaurantes ---
@admin_bp.route('/api/restaurantes', methods=['GET'])
def get_restaurantes():
    if not session.get('is_admin'): return jsonify({'message': 'Acesso negado'}), 403
    try:
        conn = conectar(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM restaurantes")
        return jsonify(cursor.fetchall()), 200
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

@admin_bp.route('/api/restaurantes', methods=['POST'])
def create_restaurante():
    if not session.get('is_admin'): return jsonify({'message': 'Acesso negado'}), 403
    f = request.form
    nome = f.get('nome')
    foto = request.files.get('foto')
    foto_url = '../static/imagens/default_restaurante.png'
    if foto:
        pasta = os.path.join('static', 'imagens')
        if not os.path.exists(pasta): os.makedirs(pasta)
        nome_arquivo = f'restaurante_{nome.replace(" ", "_")}{os.path.splitext(foto.filename)[1]}'
        foto.save(os.path.join(pasta, nome_arquivo))
        foto_url = f'/static/imagens/{nome_arquivo}'

    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("""INSERT INTO restaurantes (nome, endereco, telefone, descricao, categoria, rating, delivery_time, delivery_fee, tags, badge, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
            (nome, f.get('endereco', ''), f.get('telefone', ''), f.get('descricao', ''), f.get('categoria', 'lanches'), f.get('rating', '4.0'), f.get('delivery_time', '20-30 min'), f.get('delivery_fee', 'Grátis'), f.get('tags', '[]'), f.get('badge'), foto_url))
        conn.commit()
        return jsonify({'message': 'Restaurante criado'}), 201
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

@admin_bp.route('/api/restaurantes/<int:id>', methods=['PUT'])
def update_restaurante(id):
    if 'usuario_id' not in session or not session.get('is_admin', False):
        return jsonify({'message': 'Acesso negado'}), 403

    nome = request.form.get('nome')
    endereco = request.form.get('endereco')
    telefone = request.form.get('telefone')
    descricao = request.form.get('descricao')
    categoria = request.form.get('categoria')
    rating = request.form.get('rating')
    delivery_time = request.form.get('delivery_time')
    delivery_fee = request.form.get('delivery_fee')
    tags = request.form.get('tags')
    badge = request.form.get('badge')
    foto = request.files.get('foto')

    foto_url = None
    pasta_fotos = os.path.join('static', 'imagens')
    if foto:
        if not os.path.exists(pasta_fotos):
            os.makedirs(pasta_fotos)

        extensao = os.path.splitext(foto.filename)[1]
        nome_arquivo = f'restaurante_{nome.replace(" ", "_")}{extensao}'
        caminho_foto = os.path.join(pasta_fotos, nome_arquivo)
        foto.save(caminho_foto)
        foto_url = f'/static/imagens/{nome_arquivo}'

    try:
        conn = conectar()
        cursor = conn.cursor()

        sql = """
            UPDATE restaurantes
            SET nome=%s, endereco=%s, telefone=%s, descricao=%s, categoria=%s,
                rating=%s, delivery_time=%s, delivery_fee=%s, tags=%s, badge=%s
        """
        valores = [nome, endereco, telefone, descricao, categoria, rating, delivery_time, delivery_fee, tags, badge]

        if foto_url:
            sql += ", image=%s"
            valores.append(foto_url)

        sql += " WHERE id=%s"
        valores.append(id)

        cursor.execute(sql, valores)
        conn.commit()

        return jsonify({'message': 'Restaurante atualizado com sucesso'}), 200

    except Error as e:
        return jsonify({'message': f'Erro: {str(e)}'}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@admin_bp.route('/api/restaurantes/<int:id>', methods=['DELETE'])
def delete_restaurante(id):
    if not session.get('is_admin'): return jsonify({'message': 'Acesso negado'}), 403
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("DELETE FROM avaliacoes WHERE restaurante_id = %s", (id,))
        cursor.execute("DELETE FROM restaurantes WHERE id = %s", (id,))
        conn.commit()
        return jsonify({'message': 'Deletado'}), 200
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

# --- Clientes ---
@admin_bp.route('/api/clientes', methods=['GET'])
def get_clientes():
    if not session.get('is_admin'): return jsonify({'message': 'Acesso negado'}), 403
    try:
        conn = conectar(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email, foto_url, is_admin FROM usuarios")
        return jsonify(cursor.fetchall()), 200
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

        
@admin_bp.route('/api/clientes/<int:id>', methods=['PUT'])
def update_cliente(id):
    if 'usuario_id' not in session or not session.get('is_admin', False):
        return jsonify({'message': 'Acesso negado'}), 403
    data = request.get_json()
    nome = data.get('nome')
    is_admin = data.get('is_admin', 0)
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET nome=%s, is_admin=%s WHERE id=%s", (nome, is_admin, id))
        conn.commit()
        return jsonify({'message': 'Cliente atualizado com sucesso'}), 200
    except Error as e:
        return jsonify({'message': f'Erro: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@admin_bp.route('/api/clientes/<int:id>', methods=['DELETE'])
def delete_cliente(id):
    if 'usuario_id' not in session or not session.get('is_admin', False):
        return jsonify({'message': 'Acesso negado'}), 403
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # Primeiro, deletar dependências: assinaturas e avaliações do usuário
        cursor.execute("DELETE FROM assinaturas WHERE id_usuario = %s", (id,))
        cursor.execute("DELETE FROM avaliacoes WHERE usuario_id = %s", (id,))
        
        # Agora, deletar o usuário
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        conn.commit()
        
        return jsonify({'message': 'Cliente deletado com sucesso'}), 200
    except Error as e:
        logging.error(f"Erro ao deletar cliente {id}: {str(e)}")
        return jsonify({'message': f'Erro ao deletar cliente: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# --- Gráficos ---
@admin_bp.route('/graficos')
def graficos_page():
    if 'usuario_id' not in session or not session.get('is_admin', False):
        return redirect('/')  
    return render_template('graficos.html') 

@admin_bp.route('/api/graficos/categorias-restaurantes', methods=['GET'])
def graf_cat_res():
    conn = conectar(); cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT categoria, COUNT(*) AS total FROM restaurantes GROUP BY categoria ORDER BY total DESC")
    return jsonify(cursor.fetchall()), 200

@admin_bp.route('/api/graficos/planos-assinaturas', methods=['GET'])
def graf_planos():
    conn = conectar(); cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT plano, COUNT(*) AS total FROM assinaturas GROUP BY plano ORDER BY total DESC")
    return jsonify(cursor.fetchall()), 200

@admin_bp.route('/api/graficos/assinaturas-mensal', methods=['GET'])
def graficos_assinaturas_mensal():
    if 'usuario_id' not in session or not session.get('is_admin', False):
        return jsonify({'message': 'Acesso negado'}), 403
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT DATE_FORMAT(data_inicio, '%Y-%m') AS mes, COUNT(*) AS total
            FROM assinaturas
            GROUP BY mes
            ORDER BY mes
        """)
        dados = cursor.fetchall()
        return jsonify(dados), 200
    except Error as e:
        return jsonify({'message': f'Erro: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()