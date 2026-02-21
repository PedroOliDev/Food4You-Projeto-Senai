from flask import Blueprint, request, jsonify, session
from database import conectar
from datetime import date, timedelta
import json

biz_bp = Blueprint('biz', __name__)

PLANOS_POR_CATEGORIA = {
    "Lanches": [
        {"id": "basic", "title": "Plano Básico", "description": "Ideal para sabores", "price": "R$ 19,90", "period": "/mês", "features": ["Lanches até R$ 20,00", "Entrega grátis"], "popular": False},
        {"id": "premium", "title": "Plano Premium", "description": "Para amantes", "price": "R$ 39,90", "period": "/mês", "popular": True, "features": ["Lanches acima de R$ 30,00", "Entrega grátis"]}
    ],
    "pizzas": [
        {"id": "basic", "title": "Pizza Lover", "description": "Amantes de pizza", "price": "R$ 29,90", "period": "/mês", "features": ["20% de desconto", "Pizza grátis no aniversário"], "popular": False}
    ],
    "Italiana": [
        {"id": "basic", "title": "Plano Italiano", "price": "R$ 34,90", "period": "/mês", "features": ["20% desconto"], "popular": False}
    ],
    "Japonesa": [
        {"id": "basic", "title": "Plano Japonês", "price": "R$ 39,90", "period": "/mês", "features": ["20% desconto"], "popular": False}
    ],
    "default": [
        {"id": "basic", "title": "Plano Básico", "price": "R$ 19,90", "period": "/mês", "features": ["Descontos básicos"], "popular": False}
    ]
}

@biz_bp.route('/restaurante/<int:id>', methods=['GET'])
def get_restaurante_com_planos(id):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT nome AS name, categoria AS cuisine, image, rating, 
                   delivery_time AS deliveryTime, delivery_fee AS deliveryFee 
            FROM restaurantes WHERE id = %s
        """, (id,))
        restaurante = cursor.fetchone()
        
        if not restaurante: 
            return jsonify({'message': 'Não encontrado'}), 404
            
        # Garante que cuisine não seja None para não quebrar o .get()
        categoria = restaurante.get('cuisine') or 'default'
        restaurante['plans'] = PLANOS_POR_CATEGORIA.get(categoria, PLANOS_POR_CATEGORIA['default'])
        
        return jsonify(restaurante), 200
    except Exception as e:
        return jsonify({'message': f'Erro: {str(e)}'}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@biz_bp.route('/assinatura', methods=['POST'])
def criar_assinatura():
    if 'usuario_id' not in session: return jsonify({'message': 'Não autenticado'}), 401
    if 'restaurante_id' not in session: return jsonify({'message': 'Restaurante não selecionado'}), 400
    data = request.get_json()
    usuario_id, restaurante_id = session['usuario_id'], session['restaurante_id']
    plano = data.get('plano', 'Plano básico')

    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("""INSERT INTO assinaturas (id_usuario, restaurante_id, data_inicio, status, proximo_pagamento, dia, endereco, metodo_pagamento, detalhe_pagamento, plano)
            VALUES (%s, %s, %s, 'ativa', %s, %s, %s, %s, %s, %s)""", 
            (usuario_id, restaurante_id, date.today(), date.today()+timedelta(days=30), data.get('dia'), data.get('endereco'), data.get('metodo'), 'Pagamento Confirmado', plano))
        conn.commit()
        return jsonify({'message': 'Assinatura criada!'}), 200
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

@biz_bp.route('/avaliar', methods=['POST'])
def avaliar_restaurante():
    if 'usuario_id' not in session: return jsonify({'message': 'Não autenticado'}), 401
    data = request.get_json()
    usuario_id = session['usuario_id']
    restaurante_id, estrelas = data.get('restaurante_id'), data.get('estrelas')

    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("INSERT INTO avaliacoes (usuario_id, restaurante_id, estrelas, comentario) VALUES (%s, %s, %s, %s)", (usuario_id, restaurante_id, estrelas, data.get('comentario', '')))
        conn.commit()
        # Atualizar Média
        cursor.execute("SELECT AVG(estrelas) FROM avaliacoes WHERE restaurante_id = %s", (restaurante_id,))
        media = cursor.fetchone()[0]
        cursor.execute("UPDATE restaurantes SET rating = %s WHERE id = %s", (round(media, 1), restaurante_id))
        conn.commit()
        return jsonify({'message': 'Avaliado!'}), 201
    finally:
        if conn.is_connected(): cursor.close(); conn.close()

@biz_bp.route('/selecionar-restaurante/<int:restaurante_id>', methods=['POST'])
def selecionar_restaurante(restaurante_id):
    session['restaurante_id'] = restaurante_id
    return jsonify({'message': 'Restaurante selecionado'}), 200

@biz_bp.route('/api/restaurantes/categoria/<categoria>', methods=['GET'])
def get_restaurantes_por_categoria(categoria):
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nome AS name, endereco AS cuisine, rating, 
                   delivery_time, delivery_fee, tags, badge, image
            FROM restaurantes
            WHERE categoria = %s
        """, (categoria,))
        
        restaurantes = cursor.fetchall()
        
        # IMPORTANTE: Converter a string do banco em lista de verdade para o JS
        for r in restaurantes:
            if r['tags']:
                try:
                    r['tags'] = json.loads(r['tags'])
                except:
                    r['tags'] = []
            else:
                r['tags'] = []
                
        return jsonify(restaurantes), 200
    except Exception as e:
        return jsonify({'message': f'Erro ao carregar: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@biz_bp.route('/historico-assinaturas', methods=['GET'])
def historico_assinaturas():
    if 'usuario_id' not in session:
        return jsonify({'message': 'Não autenticado'}), 401

    usuario_id = session['usuario_id']

    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT plano, status, data_inicio AS data
            FROM assinaturas
            WHERE id_usuario = %s
            ORDER BY data_inicio DESC
        """, (usuario_id,))
        historico = cursor.fetchall()

        
        resultado = []
        for item in historico:
            resultado.append({
                'plano': item['plano'] or 'Plano básico',
                'status': item['status'].capitalize(),
                'data': str(item['data'])
            })

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'message': f'Erro ao carregar histórico: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@biz_bp.route('/assinaturas-mais-consumidas', methods=['GET'])
def assinaturas_mais_consumidas():
    if 'usuario_id' not in session:
        return jsonify({'message': 'Não autenticado'}), 401

    usuario_id = session['usuario_id']
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT plano, COUNT(*) AS total
            FROM assinaturas
            WHERE id_usuario = %s
            GROUP BY plano
            ORDER BY total DESC
            LIMIT 5
        """, (usuario_id,))
        
        resultados = cursor.fetchall()
        
        
        lista_formatada = []
        for item in resultados:
            lista_formatada.append({
                'plano': item['plano'] if item['plano'] else 'Plano Básico',
                'dias': item['total'] * 30
            })

        return jsonify(lista_formatada), 200
    except Exception as e:
        return jsonify({'message': f'Erro: {str(e)}'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()