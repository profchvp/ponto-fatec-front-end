
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
  wireMenuLinks(); // Ativa navegação interna
}

function wireMenuLinks() {
  document.querySelectorAll('[data-route]').forEach(link => {
    link.addEventListener('click', async (e) => {
      e.preventDefault();
      const route = link.getAttribute('data-route');
      switch (route) {
        case 'cadastro-professor':
          await loadPage('./pages/cadastro-professor.html');
          break;
        case 'cadastro-disciplina':
          await loadPage('./pages/cadastro-disciplina.html');
          break;
        case 'cadastro-curso':
          await loadPage('./pages/cadastro-curso.html');
          break;
        case 'cadastro-turma':
          await loadPage('./pages/cadastro-turma.html');
          break;
        case 'cadastro-sala':
          await loadPage('./pages/cadastro-sala.html');
          break;
        case 'grade':
          await loadPage('./pages/grade.html');
          break;
        case 'frequencia':
          await loadPage('./pages/frequencia.html');
          break;
        case 'cadastro-professor-massa':
          await loadPage('./pages/cadastro-professor-massa.html');
          break;

        case 'cadastro-disciplina-massa':
          await loadPage('./pages/cadastro-disciplina-massa.html');
          break;

        case 'cadastro-curso-massa':
          await loadPage('./pages/cadastro-curso-massa.html');
          break;

        case 'cadastro-turma-massa':
          await loadPage('./pages/cadastro-turma-massa.html');
          break;

        case 'cadastro-sala-massa':
          await loadPage('./pages/cadastro-sala-massa.html');
          break;
        default:
          Toast.show('Funcionalidade ainda não implementada.', 'info');
      }
    });
  });
}

async function init() {
  await Header.render();
  if (Session.isAuthenticated()) {
    await navigatePrivate();
  } else {
    await navigatePublic();
  }
}

document.addEventListener('DOMContentLoaded', init);
window.App = { init, navigatePublic, navigatePrivate };
