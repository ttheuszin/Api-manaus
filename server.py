from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)
DB_FILE = "cardapio.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_FILE):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE cardapio (
                id INTEGER PRIMARY KEY,
                item TEXT,
                preco TEXT,
                descricao TEXT
            )
        ''')
        cursor.execute("INSERT INTO cardapio (item, preco, descricao) VALUES (?,?,?)", 
                       ("Açaí 300ml", "R$ 12,00", "Com granola e leite em pó"))
        cursor.execute("INSERT INTO cardapio (item, preco, descricao) VALUES (?,?,?)", 
                       ("Açaí 500ml", "R$ 18,00", "Completo com 3 adicionais"))
        cursor.execute("INSERT INTO cardapio (item, preco, descricao) VALUES (?,?,?)", 
                       ("Barca de Açaí", "R$ 35,00", "Serve 2 pessoas"))
        conn.commit()
        conn.close()

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "produto": "Cardápio Digital Açaí",
        "dev": "ttheuszin"
    })

@app.route('/cardapio')
def get_cardapio():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cardapio')
    itens = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in itens])

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
