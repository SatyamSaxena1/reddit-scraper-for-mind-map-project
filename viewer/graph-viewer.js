const graphEl = document.querySelector('#graph');
const loadState = document.querySelector('#load-state');
const details = document.querySelector('#details');
const search = document.querySelector('#search');
const nodeCount = document.querySelector('#node-count');
const edgeCount = document.querySelector('#edge-count');
const filterButtons = [...document.querySelectorAll('[data-filter]')];
const guideClientId = document.querySelector('#guide-client-id');
const guideSavedFile = document.querySelector('#guide-saved-file');
const guideLimit = document.querySelector('#guide-limit');
const guideCommand = document.querySelector('#guide-command');
const progressFill = document.querySelector('#progress-fill');
const progressLabel = document.querySelector('#progress-label');
const appTypeButtons = [...document.querySelectorAll('[data-app-type]')];
const appTypeStep = document.querySelector('#app-type-step');
const redditFields = document.querySelector('#reddit-fields');

const colors = {
  post: '#e5b84b',
  topic: '#d64f3f',
  subreddit: '#3f9b68',
  author: '#6f7ec7',
  reddit_author: '#6f7ec7',
  index: '#f4efe4',
  entity: '#9aa6ad',
  note: '#9aa6ad'
};

let cy;
let activeFilter = 'all';
let activeAppType = 'installed';

function updateGuide() {
  const isWeb = activeAppType === 'web';
  const clientId = guideClientId.value.trim() || (isWeb ? '<your_web_app_client_id>' : '<your_installed_app_client_id>');
  const savedFile = guideSavedFile.value.trim() || 'data\\saved_posts.csv';
  const limit = Math.max(1, Number(guideLimit.value || 25));
  const previewDone = Math.max(1, Math.ceil(limit * .36));
  const secretValue = isWeb ? '<your_web_app_client_secret>' : '';
  appTypeStep.innerHTML = isWeb
    ? 'Choose <strong>web app</strong>, set redirect URI to <code>http://localhost:8080/authorize_callback</code>, then put the secret only in your local terminal.'
    : 'Choose <strong>installed app</strong>, set redirect URI to <code>http://localhost:8080/authorize_callback</code>, and keep the secret blank.';
  redditFields.innerHTML = [
    ['Name', 'reddit-mindmap-local'],
    ['Type', isWeb ? 'web app' : 'installed app'],
    ['Description', 'Local Reddit saved-post export into Obsidian notes.'],
    ['About URL', 'https://reddit-mindmap-viewer-ji7ub.ondigitalocean.app'],
    ['Redirect URI', 'http://localhost:8080/authorize_callback']
  ].map(([label, value]) => `<dt>${label}</dt><dd>${value}</dd>`).join('');
  guideCommand.textContent = [
    `$env:REDDIT_CLIENT_ID='${clientId}'`,
    `$env:REDDIT_CLIENT_SECRET='${secretValue}'`,
    `$env:REDDIT_USER_AGENT='reddit-mindmap/0.1 by your_reddit_username'`,
    `python -m reddit_mindmap scrape --oauth --saved-file "${savedFile}" --output-dir output --limit ${limit}`,
    'python -m reddit_mindmap export-vault --input-dir output --vault-dir vaults\\reddit-mindmap',
    'python -m reddit_mindmap build-graph --vault-dir vaults\\reddit-mindmap --graph-out viewer\\data\\graph.json'
  ].join('\n');
  progressFill.style.width = `${Math.min(100, Math.round((previewDone / limit) * 100))}%`;
  progressLabel.textContent = `Preview: ${previewDone} of ${limit} saved posts`;
}

function toElements(graph) {
  const nodes = graph.nodes.map((node) => ({
    data: {
      id: node.id,
      label: node.label || node.id,
      type: node.type || 'note',
      path: node.path || '',
      url: node.url || ''
    }
  }));
  const edges = graph.edges.map((edge, index) => ({
    data: {
      id: edge.id || `edge-${index}`,
      source: edge.source,
      target: edge.target,
      type: edge.type || 'links_to'
    }
  }));
  return [...nodes, ...edges];
}

function setDetails(node) {
  const data = node.data();
  const pathLine = data.path ? `<p>${data.path}</p>` : '<p>No vault path recorded.</p>';
  const obsidianLink = data.path
    ? `<p><a href="obsidian://open?path=${encodeURIComponent(data.path)}">Open in Obsidian</a></p>`
    : '';
  details.innerHTML = `
    <p class="eyebrow">${data.type}</p>
    <h2>${data.label}</h2>
    ${pathLine}
    ${obsidianLink}
  `;
}

function applyFilters() {
  if (!cy) return;
  const query = search.value.trim().toLowerCase();
  cy.nodes().forEach((node) => {
    const data = node.data();
    const matchesType = activeFilter === 'all' || data.type === activeFilter || (activeFilter === 'author' && data.type === 'reddit_author');
    const matchesSearch = !query || data.label.toLowerCase().includes(query) || data.path.toLowerCase().includes(query);
    node.style('display', matchesType && matchesSearch ? 'element' : 'none');
  });
  cy.edges().forEach((edge) => {
    const visible = edge.source().style('display') !== 'none' && edge.target().style('display') !== 'none';
    edge.style('display', visible ? 'element' : 'none');
  });
}

async function loadGraph() {
  const sources = ['data/graph.json', 'data/sample-graph.json'];
  let graph;
  for (const source of sources) {
    try {
      const response = await fetch(source, { cache: 'no-store' });
      if (response.ok) {
        graph = await response.json();
        break;
      }
    } catch (error) {
      // Try the next source.
    }
  }
  if (!graph) throw new Error('No graph data found');
  return graph;
}

loadGraph().then((graph) => {
  nodeCount.textContent = graph.nodes.length;
  edgeCount.textContent = graph.edges.length;
  cy = cytoscape({
    container: graphEl,
    elements: toElements(graph),
    wheelSensitivity: .18,
    minZoom: .12,
    maxZoom: 2.1,
    style: [
      {
        selector: 'node',
        style: {
          'background-color': (node) => colors[node.data('type')] || colors.note,
          'border-width': 2,
          'border-color': '#20252b',
          'color': '#20252b',
          'font-family': 'Georgia, Times New Roman, serif',
          'font-size': 6,
          'label': 'data(label)',
          'text-background-color': '#fffaf0',
          'text-background-opacity': .88,
          'text-background-padding': 4,
          'text-wrap': 'wrap',
          'text-max-width': 56,
          'width': (node) => node.data('type') === 'post' ? 36 : 26,
          'height': (node) => node.data('type') === 'post' ? 36 : 26
        }
      },
      {
        selector: 'edge',
        style: {
          'curve-style': 'bezier',
          'line-color': '#a9b4ad',
          'target-arrow-shape': 'triangle',
          'target-arrow-color': '#a9b4ad',
          'width': 1.5
        }
      },
      {
        selector: 'node:selected',
        style: {
          'border-width': 4,
          'border-color': '#d64f3f'
        }
      }
    ],
    layout: { name: 'preset' }
  });
  const layout = cy.layout({
    name: graph.nodes.length < 20 ? 'circle' : 'cose',
    animate: graph.nodes.length < 80,
    animationDuration: 700,
    fit: true,
    padding: 70
  });
  layout.run();
  cy.one('layoutstop', () => {
    cy.resize();
    cy.fit(undefined, 70);
    if (cy.zoom() > 2) cy.zoom(2);
  });
  setTimeout(() => {
    cy.resize();
    cy.fit(undefined, 70);
    if (cy.zoom() > 2) cy.zoom(2);
  }, 900);
  cy.on('tap', 'node', (event) => setDetails(event.target));
  loadState.classList.add('hidden');
}).catch((error) => {
  loadState.textContent = error.message;
});

filterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    activeFilter = button.dataset.filter;
    filterButtons.forEach((item) => item.setAttribute('aria-pressed', item === button ? 'true' : 'false'));
    applyFilters();
  });
});

search.addEventListener('input', applyFilters);
document.querySelector('#fit').addEventListener('click', () => cy && cy.fit(undefined, 45));
document.querySelector('#reset').addEventListener('click', () => {
  activeFilter = 'all';
  search.value = '';
  filterButtons.forEach((button) => button.setAttribute('aria-pressed', button.dataset.filter === 'all' ? 'true' : 'false'));
  applyFilters();
  if (cy) cy.fit(undefined, 45);
});

[guideClientId, guideSavedFile, guideLimit].forEach((input) => input.addEventListener('input', updateGuide));
appTypeButtons.forEach((button) => {
  button.addEventListener('click', () => {
    activeAppType = button.dataset.appType;
    appTypeButtons.forEach((item) => item.setAttribute('aria-pressed', item === button ? 'true' : 'false'));
    updateGuide();
  });
});
updateGuide();
