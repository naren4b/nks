// Read ONLY the approved PUBLIC testimonial Sheet. Never connect to form responses.
// Every testimonial must be a real, consented quote approved for its specific site.
(function () {
  'use strict';
  const cfg = window.NPANDA_PUBLIC_TESTIMONIALS || {};
  const id = String(cfg.sheetId || '');
  const site = String(cfg.siteKey || '');
  const mount = document.getElementById(String(cfg.mountId || ''));
  if (!mount || !/^[a-zA-Z0-9_-]{20,}$/.test(id) || !/^[a-z0-9-]{2,40}$/.test(site)) return;
  const section = document.getElementById(String(cfg.sectionId || ''));
  const empty = cfg.emptyId ? document.getElementById(String(cfg.emptyId)) : null;
  const fields = ['site_key', 'publish', 'permission_to_quote', 'quote', 'display_name', 'context', 'sort_order'];

  function render(items) {
    if (!items.length) return;
    mount.style.cssText = 'display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,265px),1fr));gap:16px;margin-top:24px';
    items.forEach(item => {
      const card = document.createElement('figure');
      card.style.cssText = 'margin:0;padding:22px;border:1px solid var(--line,var(--border,#cfd8dc));border-radius:16px;background:transparent';
      const quote = document.createElement('blockquote');
      quote.textContent = '\u201c' + item.quote + '\u201d';
      quote.style.cssText = 'margin:0 0 16px;font-size:1.05rem;line-height:1.6;color:inherit';
      const author = document.createElement('figcaption');
      author.textContent = item.name + (item.context ? ' | ' + item.context : '');
      author.style.cssText = 'font-weight:700;font-size:.9rem;color:inherit;opacity:.85';
      card.appendChild(quote);
      card.appendChild(author);
      mount.appendChild(card);
    });
    if (empty) empty.hidden = true;
    if (section) section.hidden = false;
  }

  let done = false;
  let script;
  let timer;
  const callbackName = 'npandaTestimonialsFeedResponse';
  function cleanup() {
    if (done) return;
    done = true;
    window.clearTimeout(timer);
    if (script) script.remove();
    try { delete window[callbackName]; } catch (_) { window[callbackName] = undefined; }
  }
  window[callbackName] = response => {
    if (done) return;
    cleanup();
    if (!response || response.status !== 'ok' || !response.table || !Array.isArray(response.table.rows)) return;
    const cols = Array.isArray(response.table.cols) ? response.table.cols : [];
    const index = Object.fromEntries(fields.map(field => [field,
      cols.findIndex(col => String(col.label || '').trim().toLowerCase() === field)]));
    // Fail closed if consent or publication headers are missing.
    if (fields.some(field => index[field] < 0)) return;
    const items = response.table.rows.map(row => {
      const get = key => {
        const cell = row.c && row.c[index[key]];
        return cell && cell.v != null ? String(cell.v).trim() : '';
      };
      return {
        site: get('site_key').toLowerCase(),
        publish: get('publish').toLowerCase(),
        permission: get('permission_to_quote').toLowerCase(),
        quote: get('quote').slice(0, 500),
        name: get('display_name').slice(0, 80) || 'Anonymous',
        context: get('context').slice(0, 110),
        order: Number(get('sort_order')) || 999
      };
    }).filter(x => x.site === site && x.publish === 'yes' && x.permission === 'yes' && x.quote)
      .sort((a, b) => a.order - b.order)
      .slice(0, Math.min(12, Math.max(1, Number(cfg.maxItems) || 4)));
    render(items);
  };
  const url = new URL('https://docs.google.com/spreadsheets/d/' + encodeURIComponent(id) + '/gviz/tq');
  url.searchParams.set('sheet', String(cfg.sheetName || 'Approved'));
  url.searchParams.set('headers', '1');
  url.searchParams.set('tqx', 'out:json;responseHandler:' + callbackName);
  url.searchParams.set('_', String(Date.now()));
  script = document.createElement('script');
  script.src = url.href;
  script.async = true;
  script.onerror = cleanup;
  timer = window.setTimeout(cleanup, 9000);
  document.head.appendChild(script);
})();
