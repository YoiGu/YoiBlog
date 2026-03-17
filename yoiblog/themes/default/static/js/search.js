// YoiBlog Client-Side Search

(function() {
  'use strict';

  let searchData = null;

  async function loadSearchIndex() {
    if (searchData) return searchData;
    try {
      const resp = await fetch('/search_index.json');
      searchData = await resp.json();
      return searchData;
    } catch (e) {
      console.error('Failed to load search index:', e);
      return [];
    }
  }

  function search(query, data) {
    if (!query || !data) return [];
    const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
    const results = [];

    for (const item of data) {
      const searchText = (item.title + ' ' + item.tags + ' ' + item.body + ' ' + item.categories).toLowerCase();
      let score = 0;

      for (const term of terms) {
        if (item.title.toLowerCase().includes(term)) score += 10;
        if (item.tags.toLowerCase().includes(term)) score += 5;
        if (item.categories.toLowerCase().includes(term)) score += 5;
        if (item.body.toLowerCase().includes(term)) score += 1;
      }

      if (score > 0) {
        results.push({ ...item, score });
      }
    }

    results.sort((a, b) => b.score - a.score);
    return results.slice(0, 20);
  }

  function renderResults(results, container) {
    if (!container) return;

    if (results.length === 0) {
      container.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:24px;">No results found.</p>';
      return;
    }

    container.innerHTML = results.map(item => `
      <div class="search-result-item">
        <div class="search-result-title"><a href="${item.url}">${escapeHtml(item.title)}</a></div>
        <div class="post-meta"><span>${item.date}</span></div>
        <div class="search-result-excerpt">${escapeHtml(item.excerpt)}</div>
      </div>
    `).join('');
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  document.addEventListener('DOMContentLoaded', async function() {
    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    if (!input || !results) return;

    const data = await loadSearchIndex();

    let debounceTimer;
    input.addEventListener('input', function() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function() {
        const query = input.value.trim();
        if (query.length < 2) {
          results.innerHTML = '';
          return;
        }
        const matches = search(query, data);
        renderResults(matches, results);
      }, 200);
    });

    // Check URL params
    const params = new URLSearchParams(window.location.search);
    const q = params.get('q');
    if (q) {
      input.value = q;
      const matches = search(q, data);
      renderResults(matches, results);
    }
  });
})();
