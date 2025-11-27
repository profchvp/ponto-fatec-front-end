
async function renderHeader() {
  const container = document.getElementById('site-header');
  const res = await fetch('./components/header.html');
  container.innerHTML = await res.text();

  const isAuth = Session.isAuthenticated();

  // Esconde/mostra links conforme login
  document.querySelectorAll('[data-route]').forEach(el => {
    el.style.display = isAuth ? 'block' : 'none';
  });

  // BRAND (lado esquerdo) - badge
  const brandUnidade = document.getElementById('brand-unidade');

  // Área do usuário (lado direito)
  const userArea = document.getElementById('user-area');

  if (!isAuth) {
    // Sem login: badge some e aparece botão de login
    if (brandUnidade) {
      brandUnidade.classList.add('d-none');
      brandUnidade.textContent = '';
    }
    userArea.innerHTML = `
      <button class="btn btn-outline-light" data-bs-toggle="modal" data-bs-target="#loginModal">
        Login
      </button>
    `;
    return;
  }

  // Autenticado: leia info da sessão
  const u = Session.getUser();
  const codigoUnidade = (u?.codigoUnidade ?? '').toString().trim();
  const nomeUnidade   = (u?.nomeUnidade ?? '').toString().trim();

  // ===== Formatar exatamente "codigo - nome"
  let textoUnidadeFormatado = '';
  if (codigoUnidade && nomeUnidade) {
    textoUnidadeFormatado = `${codigoUnidade} - ${nomeUnidade}`;
  } else if (codigoUnidade) {
    textoUnidadeFormatado = `Unidade ${codigoUnidade}`; // fallback
  } else if (nomeUnidade) {
    textoUnidadeFormatado = nomeUnidade; // fallback
  }

  // Oculta badge (não queremos duplicar)
  if (brandUnidade) {
    brandUnidade.classList.add('d-none');
    brandUnidade.textContent = '';
  }

  // Área do usuário (lado direito) — exibe nome + unidade formatada
  const unidadeSuffix = textoUnidadeFormatado ? `<div>${textoUnidadeFormatado}</div>` : '';
  userArea.innerHTML = `
    <div class="fw-semibold">${u.nomeFuncionario} (${u.numeroMatricula})</div>
    ${unidadeSuffix}
    <button class="btn btn-outline-light mt-1" id="logout-btn">Sair</button>
  `;

  document.getElementById('logout-btn').addEventListener('click', () => {
    Session.clear();
    App.navigatePublic();
    Toast.show('Sessão encerrada.', 'success');
  });
}

window.Header = { render: renderHeader };
