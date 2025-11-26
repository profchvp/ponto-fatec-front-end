# API FATEC (Flask + SQLite) — Pronta para PythonAnywhere

## Rotas Principais
- `POST /unidades` — cria unidade
- `DELETE /unidades/<codigoUnidade>` — exclui unidade (bloqueia se houver usuários)
- `POST /usuarios` — cria usuário (valida FK, hash de senha)
- `POST /auth/login` — login (retorna dados do usuário)
- `DELETE /usuarios/<emailFatec>` — exclui usuário
- `POST /unidades/import-excel` — importa unidades via Excel (`.xlsx`)

## Rodando Localmente
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
# Abra http://127.0.0.1:8000/health
```

## Deploy no PythonAnywhere (Conta Gratuita)
1. Faça upload de `app.py`, `requirements.txt` e `data/exemplo_unidades.xlsx` (opcional).
2. Em **Consoles → Bash**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Em **Web → Add a new web app → Manual configuration (Flask)**, escolha **Python 3.x**.
4. Configure o **virtualenv** como `/home/<seu-usuario>/venv`.
5. Edite o arquivo **WSGI** para apontar para o app:
   ```python
   import sys
   from pathlib import Path
   project_home = str(Path('/home/<seu-usuario>').resolve())
   if project_home not in sys.path:
       sys.path.insert(0, project_home)
   from app import app as application
   ```
6. Clique em **Reload** e teste `https://<seu-usuario>.pythonanywhere.com/health`.

## Planilha de Exemplo
Arquivo: `data/exemplo_unidades.xlsx`
Colunas: `codigoUnidade`, `nomeUnidadeFatec`, `denominacaoOficial`, `nomeDiretor`

## Exemplos de Requisição (cURL)
Veja `examples/curl.sh`.
