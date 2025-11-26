async function renderHeader() {
  const container = document.getElementById('site-header');
  const res = await fetch('./components/header.html');
  container.innerHTML = await res.text();

  const isAuth = Session.isAuthenticated();
  document.querySelectorAll('[data-route]').forEach(el => {
    el.style.display = isAuth ? 'block' : 'none';
  });

  const userArea = document.getElementById('user-area');

  // --- NÃO AUTENTICADO ---
  if (!isAuth) {
    userArea.innerHTML = `
      <button class="btn btn-outline-light" data-bs-toggle="modal" data-bs-target="#loginModal">
        Login
      </button>
    `;
    return;
  }

  // --- AUTENTICADO ---
  const u = Session.getUser();

  // CONSTRUINDO O TEXTO DA UNIDADE
  const unidadeLinha = `
    Unidade ${u.codigoUnidade ?? ''} – ${u.nomeUnidade ?? ''}
  `;

  // HTML COMPLETO DO BLOCO DO USUÁRIO
  userArea.innerHTML = `
    <div class="text-white text-end me-3" style="line-height: 1.2;">
      <div><strong>${u.nomeFuncionario}</strong> (${u.numeroMatricula})</div>
      <div>${unidadeLinha}</div>
    </div>

    <button class="btn btn-outline-light" id="logout-btn">Sair</button>
  `;

  // EVENTO LOGOUT
  document.getElementById('logout-btn').addEventListener('click', () => {
    Session.clear();
    App.navigatePublic();
    Toast.show('Sessão encerrada.', 'success');
  });
  const btn = document.getElementById("cadastrosAccordionBtn");
const content = document.getElementById("cadastrosAccordion");

if (btn && content) {
  btn.addEventListener("click", () => {
    const isOpen = btn.getAttribute("aria-expanded") === "true";

    btn.setAttribute("aria-expanded", (!isOpen).toString());
    content.style.display = isOpen ? "none" : "flex";
  });

  document.querySelectorAll("#cadastrosAccordion .accordion-link")
    .forEach(link =>
      link.addEventListener("click", () => {
        content.style.display = "none";
        btn.setAttribute("aria-expanded", "false");
      })
    );
}

}

window.Header = { render: renderHeader };
