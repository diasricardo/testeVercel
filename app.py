from flask import Flask, request, render_template, redirect, url_for, flash
import requests
import psycopg2

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"  # Para mensagens flash

# Configurações do Blob da Vercel
VERCEL_BLOB_API_URL = "https://6i6rloj4xfafhuvw.public.blob.vercel-storage.com/put"  # URL de PUT
VERCEL_BLOB_TOKEN = "store_6I6Rloj4xFaFhUVw"
HEADERS = {"Authorization": f"Bearer {VERCEL_BLOB_TOKEN}"}

# Configurações do Banco de Dados PostgreSQL (Supabase)
DB_CONFIG = {
    "host": "aws-0-sa-east-1.pooler.supabase.com",
    "user": "postgres.sguugivenyucuyfaegcl",
    "password": "uJ41uOtbuqQJXzV2",
    "database": "postgres",
    "port": "5432"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    nome = request.form.get('nome')
    foto = request.files.get('foto')

    if not nome or not foto:
        flash("Nome e foto são obrigatórios!")
        return redirect(url_for('index'))

    if not foto.mimetype.startswith('image/'):
        flash("Por favor, envie um arquivo de imagem válido.")
        return redirect(url_for('index'))

    file_path = f"uploads/{foto.filename}"
    try:
        # Faz o upload da imagem para o Blob com o método PUT
        files = {'file': (foto.filename, foto.stream, foto.mimetype)}
        response = requests.put(
            VERCEL_BLOB_API_URL,
            headers=HEADERS,
            files=files,
            data={"path": file_path, "access": "public"}
        )

        # Verificar se a conexão com o Blob foi bem-sucedida
        if response.status_code != 200:
            flash(f"Erro ao fazer upload da foto para o Blob: {response.text}")
            return redirect(url_for('index'))

        # URL pública do Blob
        blob_url = response.json().get("url")

        # Conectar ao banco de dados e salvar o nome e URL
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = "INSERT INTO pessoa (nome, foto) VALUES (%s, %s)"
            cursor.execute(query, (nome, blob_url))
            conn.commit()
            conn.close()
            flash("Dados salvos com sucesso!")
        except Exception as db_error:
            flash(f"Erro ao conectar com o banco de dados: {str(db_error)}")
            return redirect(url_for('index'))

        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Erro interno: {str(e)}")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
