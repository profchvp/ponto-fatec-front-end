async function httpPost(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    mode: 'cors',
    body: JSON.stringify(body),
  });

  const isJson = res.headers.get('content-type')?.includes('application/json');
  const data = isJson ? await res.json() : null;

  return { status: res.status, data };
}

async function httpGet(url) {
  const res = await fetch(url, { method: 'GET', mode: 'cors' });
  const isJson = res.headers.get('content-type')?.includes('application/json');
  const data = isJson ? await res.json() : null;

  return { status: res.status, data };
}

/* ========================================================
   NOVA API: PROFESSORES
   Usa httpPost e httpGet sem alterar sua estrutura atual
=========================================================== */

const API_BASE = "https://profverissimofatec.pythonanywhere.com";

const professores = {

  /**
   * POST /professores
   */
  async create(professorData) {
    const url = `${API_BASE}/professores`;
    return await httpPost(url, professorData);
  },

  /**
   * GET /professores
   */
  async listar() {
    const url = `${API_BASE}/professores`;
    return await httpGet(url);
  },

  /**
   * GET /professores/<matricula>
   */
  async obterPorMatricula(matricula) {
    const url = `${API_BASE}/professores/${matricula}`;
    return await httpGet(url);
  }
};

/* Export final */
window.Api = { httpPost, httpGet, professores };
