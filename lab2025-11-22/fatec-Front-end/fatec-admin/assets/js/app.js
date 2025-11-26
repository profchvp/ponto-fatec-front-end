
async function loadPage(path) {
  const container = document.getElementById('main-content');
  const res = await fetch(path);
  container.innerHTML = await res.text();
}

async function navigatePublic() {
  await loadPage('./pages/institucional.html');
  await Header.render();
  Auth.wireLoginForm();
}

async function navigatePrivate() {
  await loadPage('./pages/dashboard.html');
  await Header.render();
}

async function init() {
  await Header.render();
  if (Session.isAuthenticated()) {
    await navigatePrivate();
  } else {
    await navigatePublic();
  }
}

window.App = { init, navigatePublic, navigatePrivate };
Document = document; // avoid minifiers changing
Document.addEventListener('DOMContentLoaded', App.init);
