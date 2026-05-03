import sqlite3
from flask import Flask, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import pytz
import os

app = Flask(__name__)
CORS(app)
tz_manaus = pytz.timezone('America/Manaus')

def get_db():
    conn = sqlite3.connect('devs.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    # APAGA A TABELA ANTIGA SE EXISTIR
    cursor.execute('DROP TABLE IF EXISTS devs')
    cursor.execute('''
        CREATE TABLE devs (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            stack TEXT
        )
    ''')
    cursor.execute("INSERT INTO devs (nome, stack) VALUES (?,?)", ("Ada Lovelace", "Assembly"))
    cursor.execute("INSERT INTO devs (nome, stack) VALUES (?,?)", ("ttheuszin", "Python"))
    conn.commit()
    conn.close()

@app.route('/')
def status():
    try:
        init_db()
        return jsonify({
            "status": "online",
            "dev": "ttheuszin",
            "cidade": "Manaus/AM"
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/hora')
def hora():
    agora = datetime.now(tz_manaus)
    return jsonify({
        'cidade': 'Manaus',
        'hora': agora.strftime("%H:%M:%S"),
        'data': agora.strftime("%d/%m/%Y"),
        'dia_projeto': 8
    })

@app.route('/devs')
def get_devs():
    try:
        init_db()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, stack FROM devs")
        devs = [{"nome": row[0], "stack": row[1]} for row in cursor.fetchall()]
        conn.close()
        return jsonify(devs)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/cep/<cep>')
def buscar_cep(cep):
    try:
        r = requests.get(f'https://viacep.com.br/ws/{cep}/json/', timeout=10)
        dados = r.json()
        if 'erro' in dados:
            return jsonify({"erro": "CEP não encontrado"}), 404
        return jsonify(dados)
    except Exception as e:
        return jsonify({"erro": "Falha ao buscar CEP"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
