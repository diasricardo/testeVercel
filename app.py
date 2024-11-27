from flask import Flask, request, render_template, redirect, url_for, flash
import requests
import psycopg2

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"  # Para mensagens flash

# Configurações do Blob da Vercel
VERCEL_BLOB_API_URL = "https://6i6rloj4xfafhuvw.public.blob.vercel-storage.com"  # Substitua pela URL base
VERCEL_BLOB_TOKEN = "store_6I6Rloj4xFaFhUVw"  # Substitua pelo token fornecido pela Vercel
HEADERS = {"Authorization": f"Bearer {VERCEL_BLOB_TOKEN}"}  # Autenticação na API

# Configurações do Banco de Dados PostgreSQL (Supabase)
DB_CONFIG = {
    "host": "aws-0-sa-east-1.pooler.supabase.com",
    "user": "postgres.sguugivenyucuyfaegcl",
    "password": "uJ41uOtbuqQJXzV2",
    "database": "postgres",
    "port": "6543"
}


# Página inicial com formulário
@app.route('/')
def index():
    return render_template('index.html')


# Rota para processar o formulário e salvar no banco de dados
@app.route('/upload', methods=['POST'])
def upload():
    nome = request.form.get('nome')
    foto = request.files.get('foto')

    if not nome or not foto:
        flash("Nome e foto são obrigatórios!")
        return redirect(url_for('index'))

    # Faz o upload da foto para o Blob Storage (sem tentar decodificar como utf-8)
    file_path = f"uploads/{foto.filename}"  # Caminho no bucket
    try:
        # Envia a imagem como binário (sem usar .decode('utf-8'))
        response = requests.post(
            f"{VERCEL_BLOB_API_URL}/put",
            files={"file": (foto.filename, foto.stream, foto.content_type)},
            data={"path": file_path, "access": "public"},
            headers=HEADERS,
        )
        if response.status_code != 200:
            flash("Erro ao fazer upload da foto.")
            return redirect(url_for('index'))

        # URL pública da foto
        blob_url = response.json().get("url")

        # Conectar ao banco de dados PostgreSQL (Supabase) e salvar os dados
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "INSERT INTO pessoa (nome, foto) VALUES (%s, %s)"
        cursor.execute(query, (nome, blob_url))
        conn.commit()
        conn.close()

        flash("Dados salvos com sucesso!")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Erro interno: {str(e)}")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
