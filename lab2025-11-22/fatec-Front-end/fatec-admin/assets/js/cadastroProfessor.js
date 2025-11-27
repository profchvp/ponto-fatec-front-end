document.addEventListener("DOMContentLoaded", () => {
  
  const form = document.getElementById("formProfessor");
  
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      matricula: Number(document.getElementById("matricula").value),
      nomeProfessor: document.getElementById("nomeProfessor").value.trim(),
      statusSituacao: Number(document.getElementById("statusSituacao").value),
      regimeJuridico: document.getElementById("regimeJuridico").value.trim(),
      cargaHoraria: document.getElementById("cargaHoraria").value.trim(),
      horaAtividade: Number(document.getElementById("horaAtividade").value),
      HAE_O: document.getElementById("HAE_O").value.trim(),
      HAE_C: document.getElementById("HAE_C").value.trim(),
      obsManha: document.getElementById("obsManha").value.trim(),
      obsTarde: document.getElementById("obsTarde").value.trim(),
      obsNoite: document.getElementById("obsNoite").value.trim(),
    };

    console.log("Enviando dados do professor:", payload);

    // Após API pronta:
    // const { status, data } = await Api.httpPost(Config.ENDPOINTS.professores, payload);

    Toast.show("Professor salvo com sucesso!", "success");
  });

   

});
