
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'priiscila-psicopedagoga-secret')

# Armazenamento simples (para Render, sem banco). Em produção real, use banco.
DADOS_FILE = 'agendamentos.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agendar', methods=['POST'])
def agendar():
    dados = {
        'data_envio': datetime.now().isoformat(),
        'nome_paciente': request.form.get('nome_paciente'),
        'data_nascimento': request.form.get('data_nascimento'),
        'idade': request.form.get('idade'),
        'eh_menor': request.form.get('eh_menor') == 'on',
        'nome_responsavel': request.form.get('nome_responsavel'),
        'parentesco_responsavel': request.form.get('parentesco_responsavel'),
        'cpf_responsavel': request.form.get('cpf_responsavel'),
        'email_contato': request.form.get('email_contato'),
        'whatsapp': request.form.get('whatsapp'),
        'queixa_principal': request.form.get('queixa_principal'),
        'historico': request.form.get('historico'),
        'horario_preferencia': request.form.get('horario_preferencia'),
        'aceite_termos': request.form.get('aceite_termos') == 'on',
        'aceite_responsavel': request.form.get('aceite_responsavel') == 'on'
    }

    # Validação menor de idade
    try:
        idade_int = int(dados['idade'] or 0)
    except:
        idade_int = 0

    if idade_int < 18 or dados['eh_menor']:
        if not dados['nome_responsavel'] or not dados['aceite_responsavel']:
            flash('Para menores de idade, é obrigatório informar o responsável legal e autorização.', 'error')
            return redirect(url_for('index') + '#formulario')

    if not dados['aceite_termos']:
        flash('Você precisa aceitar os termos de teleatendimento.', 'error')
        return redirect(url_for('index') + '#formulario')

    # Salva
    try:
        lista = []
        if os.path.exists(DADOS_FILE):
            with open(DADOS_FILE, 'r', encoding='utf-8') as f:
                lista = json.load(f)
        lista.append(dados)
        with open(DADOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return render_template('sucesso.html', dados=dados)

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
