# app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import datetime as dt
from contextlib import contextmanager
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO

APP_DB = "db.sqlite3"

app = Flask(__name__)


# Em desenvolvimento: liberar o origin do seu front local
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]}},
     supports_credentials=False,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])



# =========================
# Helpers de Banco de Dados
# =========================
@contextmanager
def get_conn():
    conn = sqlite3.connect(APP_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")  # importante p/ FK funcionar no SQLite
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def now_iso():
    return dt.datetime.now().isoformat(timespec="seconds")

def create_tables():
    with get_conn() as conn:
        # Tabela UNIDADE
        conn.execute("""
            CREATE TABLE IF NOT EXISTS unidade (
                codigoUnidade INTEGER PRIMARY KEY,
                nomeFatecUnidade TEXT NOT NULL,
                fatecDenominacaoOficial TEXT,
                nomeDiretor TEXT,
                dataInclusao TEXT NOT NULL
            );
        """)
        # Tabela USUARIO
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuario (
                emailFatec TEXT PRIMARY KEY,
                numeroMatricula INTEGER NOT NULL,
                codigoUnidade INTEGER NOT NULL,
                nomeFuncionario TEXT NOT NULL,
                senhaLogin TEXT NOT NULL,
                indicadorAtivo INTEGER NOT NULL DEFAULT 1,
                dataInclusao TEXT NOT NULL,
                FOREIGN KEY (codigoUnidade)
                    REFERENCES unidade(codigoUnidade)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE
            );
        """)

# Cria tabelas ao iniciar o app
create_tables()
#busca a unidade a ser processada
@app.get("/unidades/<int:codigoUnidade>")
def obter_unidade_por_codigo(codigoUnidade: int):
    """
    Consulta a unidade pelo codigoUnidade.
    Retornos:
      - 200: JSON com os campos da unidade
      - 404: JSON com codigoIndicativo=404 e mensagem de não encontrada
    """
    with get_conn() as conn:
        cur = conn.execute("""
            SELECT codigoUnidade,
                   nomeFatecUnidade,
                   fatecDenominacaoOficial,
                   nomeDiretor,
                   dataInclusao
            FROM unidade
            WHERE codigoUnidade = ?
        """, (codigoUnidade,))
        row = cur.fetchone()

        if not row:
            return jsonify({
                "status": "NAO_ENCONTRADA",
                "codigoIndicativo": 404,
                "mensagem": "Unidade não encontrada",
                "codigoUnidade": codigoUnidade
            }), 404

        return jsonify({
            "status": "OK",
            "dados": {
                "codigoUnidade": row["codigoUnidade"],
                "nomeFatecUnidade": row["nomeFatecUnidade"],
                "fatecDenominacaoOficial": row["fatecDenominacaoOficial"],
                "nomeDiretor": row["nomeDiretor"],
                "dataInclusao": row["dataInclusao"]
            }
        }), 200

# ==========
# Rota Saúde
# ==========
@app.get("/health")
def health():
    return jsonify(status="ok", when=now_iso())

# ======================
# Etapa 1: Rotas Unidade
# ======================
@app.post("/unidades")
def criar_unidade():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify(erro="JSON inválido"), 400

    required = ["codigoUnidade", "nomeUnidadeFatec", "denominacaoOficial", "nomeDiretor"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify(erro=f"Campos obrigatórios ausentes: {', '.join(missing)}"), 400

    codigo = data["codigoUnidade"]
    nome = data["nomeUnidadeFatec"]
    denom = data["denominacaoOficial"]
    diretor = data["nomeDiretor"]

    with get_conn() as conn:
        # Verifica duplicidade
        cur = conn.execute("SELECT 1 FROM unidade WHERE codigoUnidade = ?", (codigo,))
        if cur.fetchone():
            return jsonify(erro="codigoUnidade já existe"), 409

        conn.execute("""
            INSERT INTO unidade (codigoUnidade, nomeFatecUnidade, fatecDenominacaoOficial, nomeDiretor, dataInclusao)
            VALUES (?, ?, ?, ?, ?)
        """, (codigo, nome, denom, diretor, now_iso()))

    return jsonify(status="OK", mensagem="Unidade cadastrada com sucesso"), 201

@app.delete("/unidades/<int:codigoUnidade>")
def excluir_unidade(codigoUnidade: int):
    try:
        with get_conn() as conn:
            cur = conn.execute("DELETE FROM unidade WHERE codigoUnidade = ?", (codigoUnidade,))
            if cur.rowcount == 0:
                return jsonify(erro="Unidade não encontrada"), 404
    except sqlite3.IntegrityError:
        # Provavelmente há usuários vinculados (FK)
        return jsonify(erro="Exclusão negada: existem usuários vinculados a esta unidade"), 409

    return jsonify(status="OK", mensagem="Unidade excluída com sucesso"), 200

# =====================
# Etapa 2: Rotas Usuário
# =====================
@app.post("/usuarios")
def criar_usuario():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify(erro="JSON inválido"), 400

    # Campos obrigatórios
    required = ["emailFatec", "codigoUnidade", "nomeFuncionario"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify(erro=f"Campos obrigatórios ausentes: {', '.join(missing)}"), 400

    email = (data.get("emailFatec") or "").strip().lower()
    codigo_unidade = data["codigoUnidade"]
    nome = data["nomeFuncionario"]
    numero_matricula = data.get("numeroMatricula")  # opcional

    # Suporta 'senhaLogin' (preferencial) ou 'senha'
    senha_clara = data.get("senhaLogin") or data.get("senha")
    if not senha_clara:
        return jsonify(erro="Campo 'senhaLogin' (ou 'senha') é obrigatório"), 400
    if len(senha_clara) < 6:
        return jsonify(erro="Senha muito curta (mínimo 6 caracteres)"), 400

    senha_hash = generate_password_hash(senha_clara, method="pbkdf2:sha256", salt_length=16)

    with get_conn() as conn:
        # Valida FK
        cur = conn.execute("SELECT 1 FROM unidade WHERE codigoUnidade = ?", (codigo_unidade,))
        if not cur.fetchone():
            return jsonify(erro="codigoUnidade inexistente (FK inválida)"), 422

        # Verifica se já existe usuário com mesmo email
        cur = conn.execute("SELECT 1 FROM usuario WHERE emailFatec = ?", (email,))
        if cur.fetchone():
            return jsonify(erro="emailFatec já cadastrado"), 409

        conn.execute("""
            INSERT INTO usuario
                (emailFatec, numeroMatricula, codigoUnidade, nomeFuncionario, senhaLogin, indicadorAtivo, dataInclusao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (email, numero_matricula, codigo_unidade, nome, senha_hash, 1, now_iso()))

    return jsonify(status="OK", mensagem="Usuario cadastrado com sucesso"), 201
#=======================================================

@app.route("/auth/login", methods=["POST", "OPTIONS"])
def login():
    from flask import request, jsonify, make_response

    # Trata preflight:
    if request.method == "OPTIONS":
        resp = make_response(("", 204))
        resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return resp

    # --- fluxo original do POST (seu código) ---
    try:
        data = request.get_json(force=True)
    except Exception:
        resp = jsonify(erro="JSON inválido")
        resp.status_code = 400
        # CORS também nas respostas de erro
        resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
        return resp

    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha")

    if not email or not senha:
        resp = jsonify(erro="Campos 'email' e 'senha' são obrigatórios")
        resp.status_code = 400
        resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
        return resp

    with get_conn() as conn:
        cur = conn.execute("""
            SELECT emailFatec, numeroMatricula, codigoUnidade, nomeFuncionario, senhaLogin, indicadorAtivo
            FROM usuario
            WHERE emailFatec = ?
        """, (email,))
        row = cur.fetchone()
        if not row:
            resp = jsonify(erro="Usuário não encontrado")
            resp.status_code = 404
            resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
            return resp

        if not bool(row["indicadorAtivo"]):
            resp = jsonify(erro="Usuário inativo")
            resp.status_code = 403
            resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
            return resp

        if not check_password_hash(row["senhaLogin"], senha):
            resp = jsonify(erro="Senha inválida")
            resp.status_code = 401
            resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
            return resp

        resp = jsonify({
            "nomeFuncionario": row["nomeFuncionario"],
            "numeroMatricula": row["numeroMatricula"],
            "codigoUnidade": row["codigoUnidade"],
            "emailFatec": row["emailFatec"]
        })
        resp.status_code = 200
        # Header CORS na resposta de sucesso
        resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
        return resp

#================================================
@app.delete("/usuarios/<path:emailFatec>")
def excluir_usuario(emailFatec: str):
    email = (emailFatec or "").strip().lower()
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM usuario WHERE emailFatec = ?", (email,))
        if cur.rowcount == 0:
            return jsonify(erro="Usuário não encontrado"), 404
    return jsonify(status="OK", mensagem="Usuário excluído com sucesso"), 200

# ===========================================
# (Opcional) Importação de UNIDADES via Excel
# ===========================================
@app.post("/unidades/import-excel")
def importar_unidades_excel():
    """
    Envie um arquivo .xlsx com as colunas:
    codigoUnidade, nomeUnidadeFatec, denominacaoOficial, nomeDiretor
    """
    if "file" not in request.files:
        return jsonify(erro="Envie o arquivo em multipart/form-data no campo 'file'"), 400

    excel_file = request.files["file"]

    try:
        import pandas as pd
    except Exception:
        return jsonify(
            erro="Dependências ausentes para Excel. Instale 'pandas' e 'openpyxl'."
        ), 501

    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        return jsonify(erro=f"Falha ao ler Excel: {e}"), 400

    expected_cols = {"codigoUnidade", "nomeUnidadeFatec", "denominacaoOficial", "nomeDiretor"}
    if not expected_cols.issubset(set(df.columns)):
        return jsonify(
            erro=f"Colunas esperadas: {sorted(expected_cols)}. Colunas encontradas: {sorted(df.columns.tolist())}"
        ), 400

    inseridos, ignorados = 0, 0
    with get_conn() as conn:
        for _, row in df.iterrows():
            codigo = int(row["codigoUnidade"])
            nome = str(row["nomeUnidadeFatec"])
            denom = None if pd.isna(row["denominacaoOficial"]) else str(row["denominacaoOficial"])
            diretor = None if pd.isna(row["nomeDiretor"]) else str(row["nomeDiretor"])

            cur = conn.execute("SELECT 1 FROM unidade WHERE codigoUnidade = ?", (codigo,))
            if cur.fetchone():
                ignorados += 1
                continue

            conn.execute("""
                INSERT INTO unidade (codigoUnidade, nomeFatecUnidade, fatecDenominacaoOficial, nomeDiretor, dataInclusao)
                VALUES (?, ?, ?, ?, ?)
            """, (codigo, nome, denom, diretor, now_iso()))
            inseridos += 1

    return jsonify(status="OK", inseridos=inseridos, ignorados=ignorados), 200

if __name__ == "__main__":
    # Para rodar localmente: python app.py
    app.run(host="0.0.0.0", port=8000, debug=True)