#!/usr/bin/env bash
set -euo pipefail
BASE="http://127.0.0.1:8000"

# Health
echo "Health:"; curl -s "$BASE/health"; echo -e "
"

# Criar unidade
curl -s -X POST "$BASE/unidades"   -H 'Content-Type: application/json'   -d '{
    "codigoUnidade": 10,
    "nomeUnidadeFatec": "Fatec São Paulo",
    "denominacaoOficial": "Faculdade de Tecnologia de São Paulo",
    "nomeDiretor": "Fulano de Tal"
  }'; echo -e "
"

# Criar usuário
curl -s -X POST "$BASE/usuarios"   -H 'Content-Type: application/json'   -d '{
    "emailFatec": "alguem@fatec.sp.gov.br",
    "codigoUnidade": 10,
    "nomeFuncionario": "Maria Almeida",
    "senhaLogin": "SenhaForte123",
    "numeroMatricula": "2025001"
  }'; echo -e "
"

# Login
curl -s -X POST "$BASE/auth/login"   -H 'Content-Type: application/json'   -d '{
    "email": "alguem@fatec.sp.gov.br",
    "senha": "SenhaForte123"
  }'; echo -e "
"

# Excluir usuário
curl -s -X DELETE "$BASE/usuarios/alguem@fatec.sp.gov.br"; echo -e "
"

# Excluir unidade
curl -s -X DELETE "$BASE/unidades/10"; echo -e "
"
