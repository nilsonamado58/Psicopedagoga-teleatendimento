
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'priscila-psicopedagoga-secret')

DADOS_FILE = 'agendamentos.json'

# CONFIGURAÇÃO DE E-MAIL - ALTERE AQUI NO VSCODE
EMAIL_DESTINO_PSICOPEDAGOGA = "priscila_amado84@yahoo.com"  # <-- Email da psicopedagoga que receberá os dados
EMAIL_REMETENTE = os.environ.get('EMAIL_REMETENTE', 'priscila_amado84@yahoo.com')  # pode usar mesmo Yahoo ou Gmail
EMAIL_SENHA_APP = os.environ.get('EMAIL_SENHA_APP', '')  # Senha de app do Yahoo/Gmail - configurar no Render
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.mail.yahoo.com')  # Yahoo: smtp.mail.yahoo.com | Gmail: smtp.gmail.com
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))

def enviar_email_psicopedagoga(dados):
    """
    Envia dados do paciente e responsável para priscila_amado84@yahoo.com
    para aguardar confirmação de pagamento PIX 33075478873 e agendar teleatendimento
    """
    # Se não houver senha configurada, apenas loga (não quebra o agendamento)
    if not EMAIL_SENHA_APP:
        print(f"[AVISO] EMAIL_SENHA_APP não configurado. Dados salvos mas e-mail não enviado. Destino: {EMAIL_DESTINO_PSICOPEDAGOGA}")
        print(f"Dados: {dados}")
        return False

    try:
        # Monta corpo do e-mail com dados do paciente e responsável
        assunto = f"🔔 Novo Agendamento Teleatendimento - {dados['nome_paciente']} - 30min R$150"

        corpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #6C5CE7;">Novo Agendamento - Teleatendimento Psicopedagógico</h2>
            <p><strong>Data do envio:</strong> {dados['data_envio']}</p>
            <p><strong>Sessão:</strong> 30 minutos | Valor: R$150,00 | PIX: 33075478873</p>
            <hr>
            <h3>👤 Dados do Paciente</h3>
            <ul>
                <li><strong>Nome:</strong> {dados['nome_paciente']}</li>
                <li><strong>Idade:</strong> {dados['idade']}</li>
                <li><strong>Data Nascimento:</strong> {dados['data_nascimento']}</li>
                <li><strong>WhatsApp:</strong> {dados['whatsapp']}</li>
                <li><strong>E-mail contato:</strong> {dados['email_contato']}</li>
                <li><strong>Queixa principal:</strong> {dados['queixa_principal']}</li>
                <li><strong>Histórico:</strong> {dados['historico']}</li>
                <li><strong>Horário preferência:</strong> {dados['horario_preferencia']}</li>
                <li><strong>É menor?</strong> {'SIM' if dados['eh_menor'] else 'NÃO'}</li>
            </ul>
            <hr>
            <h3>👨‍👩‍👧 Dados do Responsável Legal (se menor)</h3>
            <ul>
                <li><strong>Nome responsável:</strong> {dados['nome_responsavel'] or 'Não informado (maior de idade)'}</li>
                <li><strong>Parentesco:</strong> {dados['parentesco_responsavel'] or '-'}</li>
                <li><strong>CPF responsável:</strong> {dados['cpf_responsavel'] or '-'}</li>
                <li><strong>Autorizou presença:</strong> {'SIM' if dados['aceite_responsavel'] else 'NÃO / Não se aplica'}</li>
            </ul>
            <hr>
            <h3 style="color: #C0392B;">💳 Aguardando confirmação de pagamento</h3>
            <p>PIX: <b>33075478873</b> - Titular: Priscila A. S. Moreira<br>
            Valor: R$150,00 por sessão de 30 minutos<br>
            Paciente deve identificar nome no PIX e enviar comprovante no WhatsApp {dados['whatsapp']}</p>
            <hr>
            <p style="font-size: 12px; color: #888;">E-mail automático gerado pela landing page teleatendimento-psicopedagoga<br>
            Contato oficial: priscila_amado84@yahoo.com</p>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = EMAIL_DESTINO_PSICOPEDAGOGA
        msg.attach(MIMEText(corpo_html, "html", "utf-8"))

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(EMAIL_REMETENTE, EMAIL_SENHA_APP)
            server.sendmail(EMAIL_REMETENTE, EMAIL_DESTINO_PSICOPEDAGOGA, msg.as_string())

        print(f"E-mail enviado com sucesso para {EMAIL_DESTINO_PSICOPEDAGOGA} - Paciente: {dados['nome_paciente']}")
        return True

    except Exception as e:
        print(f"ERRO ao enviar e-mail para {EMAIL_DESTINO_PSICOPEDAGOGA}: {e}")
        # Não quebra o fluxo, agendamento já foi salvo
        return False

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

    # Salva localmente (backup)
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

    # NOVO: Envia e-mail para psicopedagoga com dados do paciente e responsável
    # Email: priscila_amado84@yahoo.com para aguardar confirmação pagamento PIX 33075478873
    enviar_email_psicopedagoga(dados)

    return render_template('sucesso.html', dados=dados)

@app.route('/health')
def health():
    return {'status': 'ok', 'email_destino': EMAIL_DESTINO_PSICOPEDAGOGA}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
