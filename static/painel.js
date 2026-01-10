console.log('painel.js carregado');

// Ícones por categoria
const iconesCategorias = {
  "Beleza": "💄", "Esportes": "🏀", "Moda": "👗", "Eletrônicos": "📱",
  "Casa": "🏠", "Alimentos": "🍔", "Livros": "📚", "Brinquedos": "🧸", "Outros": "🔥"
};

// Estado
let ofertasCarregadas = [];
let paginaAtual = 1;
const ofertasPorPagina = 9;
let graficoCategorias, graficoPrecos, graficoLojas;
let idEdicaoAtual = null;
const favoritos = new Set(JSON.parse(localStorage.getItem('favoritos') || '[]'));

// Toast notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}

// Auth + carga inicial
(function initAuth() {
  const token = localStorage.getItem('token');
  if (token) return carregarOfertas(token);

  fetch("http://localhost:5000/usuarios/login", {
    method: 'POST',
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: 'ofertasdoparceiroorlando@gmail.com', senha: 'residencial7068.' })
  })
  .then(r => r.json())
  .then(a => { localStorage.setItem('token', a.token); carregarOfertas(a.token); })
  .catch(() => showToast("Erro no login", "error"));
})();

// Modo escuro
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('toggleDark').addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
  });
});

// Carregar ofertas
function carregarOfertas(token) {
  fetch("http://localhost:5000/ofertas/todas", { headers: { Authorization: `Bearer ${token}` } })
    .then(r => r.json())
    .then(ofertas => {
      ofertasCarregadas = ofertas;
      paginaAtual = 1;
      renderizarOfertas(ofertasCarregadas);
      atualizarDashboard(ofertasCarregadas);
    })
    .catch(() => showToast("Erro ao carregar ofertas", "error"));
}

// Dashboard
function atualizarDashboard(ofertas) {
  atualizarGraficoCategorias(ofertas);
  atualizarGraficoPrecos(ofertas);
  atualizarGraficoLojas(ofertas);
}

// Gráficos dinâmicos
function atualizarGraficoCategorias(ofertas) {
  const contagem = {};
  ofertas.forEach(o => contagem[o.categoria] = (contagem[o.categoria] || 0) + 1);
  const ctx = document.getElementById('graficoCategorias').getContext('2d');
  if (graficoCategorias) graficoCategorias.destroy();
  graficoCategorias = new Chart(ctx, {
    type: 'bar',
    data: { labels: Object.keys(contagem), datasets: [{ data: Object.values(contagem), backgroundColor: ['#e0f7fa','#fce4ec','#f3e5f5','#e8f5e9','#fff9c4','#ffe0b2','#d7ccc8','#c5cae9','#eeeeee'] }] },
    options: { responsive: true, plugins: { legend: { display: false } } }
  });
}

function atualizarGraficoPrecos(ofertas) {
  const soma = {}, cont = {};
  ofertas.forEach(o => { soma[o.categoria] = (soma[o.categoria] || 0) + parseFloat(o.preco); cont[o.categoria] = (cont[o.categoria] || 0) + 1; });
  const labels = Object.keys(soma);
  const medias = labels.map(l => soma[l] / cont[l]);
  const ctx = document.getElementById('graficoPrecos').getContext('2d');
  if (graficoPrecos) graficoPrecos.destroy();
  graficoPrecos = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets: [{ data: medias, label: 'Preço médio (R$)', backgroundColor: ['#e0f7fa','#fce4ec','#f3e5f5','#e8f5e9','#fff9c4','#ffe0b2','#d7ccc8','#c5cae9','#eeeeee'] }] },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
  });
}

function atualizarGraficoLojas(ofertas) {
  const soma = {}, cont = {};
  ofertas.forEach(o => { soma[o.loja] = (soma[o.loja] || 0) + parseFloat(o.preco); cont[o.loja] = (cont[o.loja] || 0) + 1; });
  const labels = Object.keys(soma);
  const medias = labels.map(l => soma[l] / cont[l]);
  const ctx = document.getElementById('graficoLojas').getContext('2d');
  if (graficoLojas) graficoLojas.destroy();
  graficoLojas = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets: [{ data: medias, label: 'Média por loja (R$)', borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,0.2)', tension: 0.3 }] },
    options: { responsive: true, plugins: { legend: { display: true } }, scales: { y: { beginAtZero: true } } }
  });
}

// Renderização com paginação
function renderizarOfertas(ofertas) {
  const container = document.getElementById('alertas');
  container.innerHTML = '';

  const inicio = (paginaAtual - 1) * ofertasPorPagina;
  const fim = inicio + ofertasPorPagina;
  const pagina = ofertas.slice(inicio, fim);

  pagina.forEach(oferta => {
    const card = document.createElement('div');
    card.classList.add('card', oferta.categoria.toLowerCase());
    card.setAttribute('data-id', oferta.id);
    card.setAttribute('data-categoria', oferta.categoria);
    card.setAttribute('data-loja', oferta.loja);
    card.setAttribute('data-preco', oferta.preco);

    const icone = iconesCategorias[oferta.categoria] || iconesCategorias["Outros"];
    const fav = favoritos.has(oferta.id);

    card.innerHTML = `
      <h4>${icone} ${oferta.titulo}</h4>
      <p><strong>Loja:</strong> ${oferta.loja}</p>
      <p><strong>Preço:</strong> R$ ${parseFloat(oferta.preco).toFixed(2)}</p>
      <p><strong>Categoria:</strong> ${oferta.categoria}</p>
      <div class="card-actions">
        <button class="accent" data-acao="favorito">${fav ? '★ Favorito' : '☆ Favoritar'}</button>
        <button class="secondary" data-acao="editar">✏️ Editar</button>
        <button class="danger" data-acao="excluir">🗑️ Excluir</button>
      </div>
    `;
    container.appendChild(card);
  });

  document.getElementById('paginaInfo').innerText = `Página ${paginaAtual} de ${Math.ceil(ofertas.length / ofertasPorPagina)}`;

  container.querySelectorAll('.card-actions button').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const acao = e.target.getAttribute('data-acao');
      const card = e.target.closest('.card');
      const id = card.getAttribute('data-id');
      if (acao === 'favorito') toggleFavorito(id, e.target);
      if (acao === 'editar') abrirModalEdicao(id);
      if (acao === 'excluir') excluirOferta(id);
    });
  });
}

// Favoritos
function toggleFavorito(id, btn) {
  if (favoritos.has(id)) {
    favoritos.delete(id);
    btn.textContent = '☆ Favoritar';
    showToast("Removido dos favoritos", "info");
  } else {
    favoritos.add(id);
    btn.textContent = '★ Favorito';
    showToast("Adicionado aos favoritos", "success");
  }
  localStorage.setItem('favoritos', JSON.stringify([...favoritos]));
}

// Botão voltar ao topo
const btnTopo = document.getElementById('btnTopo');
window.addEventListener('scroll', () => {
  if (document.documentElement.scrollTop > 200) {
    btnTopo.style.display = 'flex';
  } else {
    btnTopo.style.display = 'none';
  }
});
btnTopo.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});
