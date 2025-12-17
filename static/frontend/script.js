const API_URL = "http://127.0.0.1:8000";
let currentTicker = "";
let currentMode = "fechamento";
let chartInstance = null; // Única variável para controlar o gráfico
let assetData = null;
let allTickers = [];

/**
 * 1. INICIALIZAÇÃO
 */
async function fetchAssets() {
  try {
    const response = await fetch(`${API_URL}/ativos`);
    const data = await response.json();
    allTickers = data.ativos;
    renderAssetList(allTickers);
    setupSearch();
  } catch (err) {
    console.error("Erro ao conectar com API:", err);
  }
}

function renderAssetList(tickers) {
  const listEl = document.getElementById("lista-ativos");
  listEl.innerHTML = "";
  tickers.forEach((ticker) => {
    const li = document.createElement("li");
    li.className =
      "sidebar-item p-5 cursor-pointer flex justify-between items-center text-sm font-medium text-gray-400";
    li.innerHTML = `<span>${ticker}</span> <span class="text-[10px] text-gray-800 font-bold">VIEW</span>`;
    li.onclick = () => loadAsset(ticker);
    listEl.appendChild(li);
  });
}

function setupSearch() {
  const searchInput = document.getElementById("search-input");
  searchInput.addEventListener("input", (e) => {
    const searchTerm = e.target.value.toUpperCase();
    const filteredTickers = allTickers.filter((ticker) =>
      ticker.includes(searchTerm)
    );
    renderAssetList(filteredTickers);
  });
}

/**
 * 2. CARREGAMENTO DE DADOS (Ao clicar no ativo)
 */
async function loadAsset(ticker) {
  currentTicker = ticker;

  // Interface
  document.getElementById("welcome-view").classList.add("hidden");
  document.getElementById("dashboard-view").classList.remove("hidden");
  document.getElementById("active-ticker").innerText = ticker;

  try {
    const response = await fetch(`${API_URL}/ativos/${ticker}`);
    assetData = await response.json();

    // Sempre que carregar um novo ativo, renderiza o gráfico com o modo atual
    renderChart();
  } catch (err) {
    console.error("Erro ao carregar ativo:", err);
  }
}

/**
 * 3. LÓGICA DE BOTÕES (Ao trocar tipo de gráfico)
 */
function updateDisplay(mode) {
  currentMode = mode;

  // Atualiza visual dos botões
  document
    .querySelectorAll(".btn-toggle")
    .forEach((b) => b.classList.remove("active"));
  const activeBtn = document.getElementById(`btn-${mode}`);
  if (activeBtn) activeBtn.classList.add("active");

  // Re-renderiza o gráfico com os dados que já temos na memória
  renderChart();
}

function renderChart() {
  if (!assetData || !currentTicker) return;

  const canvas = document.getElementById("mainChart");
  const ctx = canvas.getContext("2d");

  // 1. LIMPEZA ABSOLUTA: Destrói qualquer instância anterior para evitar o erro de Canvas
  if (chartInstance instanceof Chart) {
    chartInstance.destroy();
    chartInstance = null;
  }

  // 2. PREPARAÇÃO DE DADOS
  // const labels = assetData.map((d) =>
  //   new Date(d.data_pregao).toLocaleDateString()
  // );
  const labels = assetData.map((d) => {
    // Se d.data_pregao já for "2025-01-02", o split garante o formato BR
    const data = d.data_pregao.split("-");
    return `${data[2]}/${data[1]}/${data[0]}`; // Retorna DD/MM/YYYY
  });
  const values = assetData.map((d) => d[currentMode]);
  const isVolume = currentMode === "volume";

  // 3. CONFIGURAÇÃO DO GRÁFICO
  chartInstance = new Chart(ctx, {
    type: isVolume ? "bar" : "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: `${currentMode.toUpperCase()} - ${currentTicker}`,
          data: values,
          borderColor: isVolume ? "#3b82f6" : "#facc15",
          backgroundColor: isVolume
            ? "rgba(59, 130, 246, 0.3)"
            : "rgba(250, 204, 21, 0.1)",
          borderWidth: 2,
          fill: true,
          tension: 0.3,
          pointRadius: 0,
          pointHoverRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: "index",
      },
      plugins: {
        legend: { display: false },
        // --- CONFIGURAÇÃO DE ZOOM E PAN ---
        zoom: {
          pan: {
            enabled: true,
            mode: "x",
          },
          zoom: {
            wheel: { enabled: true }, // Zoom com Scroll
            drag: {
              enabled: true, // Zoom com Seleção (Clique e Arraste)
              backgroundColor: "rgba(250, 204, 21, 0.2)",
              borderColor: "#facc15",
              borderWidth: 1,
            },
            mode: "x",
          },
        },
        tooltip: {
          backgroundColor: "#171717",
          titleColor: "#facc15",
          bodyColor: "#fff",
          borderColor: "#333",
          borderWidth: 1,
          titleFont: { family: "JetBrains Mono" },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            color: "#666",
            font: { family: "JetBrains Mono", size: 10 },
          },
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: {
            color: "#666",
            font: { family: "JetBrains Mono", size: 10 },
          },
        },
      },
    },
  });

  // 4. ATUALIZAÇÃO DO BOTÃO DE DOWNLOAD
  setupDownloadTrigger();
}

/**
 * Função auxiliar para resetar o zoom via botão
 */
function resetZoom() {
  if (chartInstance) {
    chartInstance.resetZoom();
  }
}

function setupDownloadTrigger() {
    const btn = document.getElementById("btn-download");
    if (btn) {
        btn.onclick = () => {
            // Captura o elemento canvas
            const canvas = document.getElementById("mainChart");
            
            // Cria um link temporário para download da imagem gerada pelo Chart.js
            const link = document.createElement('a');
            link.download = `grafico_${currentTicker}_${currentMode}.png`;
            
            // Converte o canvas para base64 (PNG)
            link.href = canvas.toDataURL('image/png');
            
            // Simula o clique
            link.click();
        };
    }
}

/**
 * 5. DOWNLOAD
 */
function setupDownload() {
  const btn = document.getElementById("btn-download");
  if (btn) {
    btn.onclick = () => {
      const downloadUrl = `${API_URL}/ativos/${currentTicker}/graficos?tipo=${currentMode}`;
      window.open(downloadUrl, "_blank");
    };
  }
}

/**
 * 5. RESET ZOOM
 */
function resetZoom() {
  if (chartInstance) {
    chartInstance.resetZoom();
  }
}

window.onload = fetchAssets;
