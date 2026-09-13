'use strict';
(() => {
  const search = document.getElementById('catalog-search');
  const cards = [...document.querySelectorAll('.demo-card')];
  const buttons = [...document.querySelectorAll('[data-filter]')];
  let group = 'all';
  function filter() {
    const query = search.value.trim().toLowerCase();
    let count = 0;
    for (const card of cards) {
      card.hidden = !(group === 'all' || card.dataset.group === group) || !card.textContent.toLowerCase().includes(query);
      if (!card.hidden) count++;
    }
    document.getElementById('catalog-count').textContent = count ? `${count} lab${count === 1 ? '' : 's'}` : 'No matching labs';
  }
  search.addEventListener('input', filter);
  for (const b of buttons) b.onclick = () => { group = b.dataset.filter; buttons.forEach(el => el.setAttribute('aria-pressed', String(el === b))); filter(); };
})();
