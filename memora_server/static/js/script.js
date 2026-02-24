function confirmarRemocao(item = "plano") {
    return confirm(`Tem certeza de que deseja apagar este ${item}?`);
}

function confirmarUndo(item = "plano") {
    return confirm(`Tem certeza de que quer mover o/a ${item} para a lista de planejados?`)
}

function atualizarNomeArquivo(input) {
    const textoElemento = document.getElementById('texto-arquivo');

    if (input.files && input.files.length > 0) {
        textoElemento.textContent = input.files[0].name;
        textoElemento.style.color = "#cbd5e1";
    } else {
        textoElemento.textContent = "Nenhum arquivo escolhido";
        textoElemento.style.color = "#94a3b8";
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
        texto.textContent = input.files[0].name;
        box.classList.add('has-file');
    } else {
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

function abrirLightbox(caminhoImagem) {
    const lightbox = document.getElementById('lightbox');
    const img = document.getElementById('lightbox-img');

    img.src = caminhoImagem;

    lightbox.style.display = 'flex';
}

function fecharLightbox() {
    document.getElementById('lightbox').style.display = 'none';
}

function adicionarCampoCidade() {
    const container = document.getElementById('cities-container');

    const div = document.createElement('div');
    div.className = 'city-input-group';

    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'cidades';
    input.placeholder = 'Nome da cidade';
    input.required = true;
    input.autocomplete = 'off';

    const btnRemove = document.createElement('button');
    btnRemove.type = 'button';
    btnRemove.className = 'btn-remove-city';
    btnRemove.innerHTML = '×';
    btnRemove.onclick = function() {
        container.removeChild(div);
    };

    div.appendChild(input);
    div.appendChild(btnRemove);
    container.appendChild(div);
}