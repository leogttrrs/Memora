function confirmarRemocao(item = "plano") {
    return confirm(`Tem certeza de que deseja apagar este ${item}?`);
}

function atualizarNomeArquivo(input) {
    const textoElemento = document.getElementById('texto-arquivo');

    if (input.files && input.files.length > 0) {
        // Pega o nome do arquivo (ex: "batman.jpg")
        textoElemento.textContent = input.files[0].name;
        textoElemento.style.color = "#cbd5e1"; // Muda cor para branco/claro
    } else {
        // Se cancelou
        textoElemento.textContent = "Nenhum arquivo escolhido";
        textoElemento.style.color = "#94a3b8"; // Volta para cinza
    }
}

function toggleForm(show) {
    const container = document.querySelector('.screens-container');
    if (show) {
        container.classList.add('show-form');
    } else {
        container.classList.remove('show-form');
    }
}

function atualizarInput(input) {
    const box = document.getElementById('file-box');
    const texto = document.getElementById('file-text');

    if (input.files && input.files.length > 0) {
        // Muda o texto e ativa o Slide
        texto.textContent = input.files[0].name;
        box.classList.add('has-file'); // <--- ISSO DISPARA A ANIMAÇÃO CSS
    } else {
        // Reseta
        texto.textContent = "Selecione uma imagem...";
        box.classList.remove('has-file');
    }
}

function abrirModalNota() {
    document.getElementById('modal-nota-overlay').style.display = 'flex';

    setTimeout(() => {
        document.querySelector('.modal-box input[type="number"]').focus();
    }, 100);
}

function fecharModalNota() {
    document.getElementById('modal-nota-overlay').style.display = 'none';
}

document.getElementById('modal-nota-overlay').addEventListener('click', function(e) {
    if (e.target === this) {
        fecharModalNota();
    }
});