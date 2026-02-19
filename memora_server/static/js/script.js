function confirmarRemocao(item = "plano") {
    return confirm(`Tem certeza de que deseja apagar este ${item}?`);
}

function confirmarUndo(item = "plano") {
    return confirm(`Tem certeza de que quer mover o/a ${item} para a lista de planejados?`)
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

// Função para abrir o Lightbox
function abrirLightbox(caminhoImagem) {
    const lightbox = document.getElementById('lightbox');
    const img = document.getElementById('lightbox-img');

    // Define a imagem que foi clicada
    img.src = caminhoImagem;

    // Mostra o overlay
    lightbox.style.display = 'flex';
}

// Função para fechar (clicando no fundo ou no X)
function fecharLightbox() {
    document.getElementById('lightbox').style.display = 'none';
}

function adicionarCampoCidade() {
    const container = document.getElementById('cities-container');

    // Cria a div que envolve (wrapper)
    const div = document.createElement('div');
    div.className = 'city-input-group';

    // Cria o input novo
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'cidades'; // O segredo está aqui: mesmo nome!
    input.placeholder = 'Nome da cidade';
    input.required = true;
    input.autocomplete = 'off';

    // Cria o botão de remover (X)
    const btnRemove = document.createElement('button');
    btnRemove.type = 'button';
    btnRemove.className = 'btn-remove-city';
    btnRemove.innerHTML = '×';
    btnRemove.onclick = function() {
        container.removeChild(div);
    };

    // Monta tudo
    div.appendChild(input);
    div.appendChild(btnRemove);
    container.appendChild(div);
}