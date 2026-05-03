import sqlite3
from flask import Flask, jsonify
import requests
from datetime import datetime
import pytz
# CRIA BANCO E TABELA SE NÃO EXISTIR
conexao = sqlite3.connect('devs.db')
cursor = conexao.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS devs (
    login TEXT PRIMARY KEY,
    nome TEXT,
    seguidores INTEGER,
    repos INTEGER,
    criado_em TEXT
)
''')
conexao.commit()
conexao.close()
app = Flask(__name__)
tz_manaus = pytz.timezone('America/Manaus')


@app.route('/hora')
def hora():
    agora = datetime.now(tz_manaus)
    return jsonify({
        'cidade': 'Manaus',
        'hora': agora.strftime("%H:%M:%S"),
        'data': agora.strftime("%d/%m/%Y"),
        'dia_projeto': 5,
        'status': 'Online',
        'dev':"ttheuszin"
    })

@app.route('/cep/<cep>')
def buscar_cep(cep):
    try:
        url = f'https://viacep.com.br/ws/{cep}/json/'
        resposta = requests.get(url, timeout=15)
        dados = resposta.json()
        
        if 'erro' in dados:
            return jsonify({'erro': 'CEP não encontrado'}), 404
            
        return jsonify({
            'cep': dados['cep'],
            'logradouro': dados['logradouro'],
            'bairro': dados['bairro'],
            'cidade': dados['localidade'],
            'uf': dados['uf'],
            'ddd': dados['ddd'],
            'consultado_em': datetime.now(tz_manaus).strftime("%d/%m/%Y %H:%M"),
            'dev':"ttheuszin"
        })
    except:
        return jsonify({'erro': 'Falha ao consultar CEP'}), 500

@app.route('/clima')
def clima():
    try:
        url = 'https://api.open-meteo.com/v1/forecast?latitude=-3.1&longitude=-60.0&current_weather=true'
        resposta = requests.get(url, timeout=15)
        dados = resposta.json()
        
        temp = dados['current_weather']['temperature']
        return jsonify({
            'cidade': 'Manaus',
            'temperatura': f'{temp}°C',
            'vento': f"{dados['current_weather']['windspeed']} km/h",
            'atualizado_em': datetime.now(tz_manaus).strftime("%H:%M"),
            'dev':"ttheuszin"
        })
    except:
        return jsonify({'erro': 'Sem clima - timeout Open-Meteo'}), 500

@app.route('/github/<usuario>')
def github(usuario):
    try:
        url = f'https://api.github.com/users/{usuario}'
        headers = {'User-Agent': 'api-manaus-app'}
        resposta = requests.get(url, headers=headers, timeout=15)
        dados = resposta.json()
        
        if dados.get('message') == 'Not Found':
            return jsonify({'erro': 'Usuário não encontrado'}), 404
                    # SALVA NO BANCO
        conexao = sqlite3.connect('devs.db')
        cursor = conexao.cursor()
        cursor.execute('INSERT OR REPLACE INTO devs VALUES (?,?,?,?,?)', 
                       (dados["login"], dados["name"], dados["followers"], dados["public_repos"], dados["created_at"][:10]))
        conexao.commit()
        conexao.close()
        return jsonify({
            'login': dados['login'],
            'nome': dados['name'],
            'bio': dados['bio'],
            'repos_publicos': dados['public_repos'],
            'seguidores': dados['followers'],
            'seguindo': dados['following'],
            'avatar': dados['avatar_url'],
            'criado_em': dados['created_at'][:10],
            'dev': usuario,
        })
    except:
        return jsonify({'erro': 'Falha ao buscar GitHub'}), 500
@app.route("/historico")
def historico():
    conexao = sqlite3.connect('devs.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM devs')
    devs = cursor.fetchall()
    conexao.close()
    lista = [{"login": d[0], "nome": d[1], "seguidores": d[2], "repos": d[3], "criado_em": d[4]} for d in devs]
    return jsonify({"total": len(lista), "devs": lista})
@app.route("/")
def index():
    return {
        "api": "Manaus API",
        "status": "online",
        "dev": "ttheuszin",
        "cidade": "Manaus/AM",
        "endpoints_funcionando": [
            "/historico",
            "/cep/69020001"
        ],
        "endpoints_instaveis_free": [
            "/clima",
            "/github/usuario"
        ]
    }
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
