/* Lineage of the Church - behaviour */
(function(){
  var uf = ("onbeforematch" in HTMLElement.prototype);
  if (uf) document.documentElement.classList.add('uf');
  else document.querySelectorAll('[hidden="until-found"]').forEach(function(el){ el.setAttribute('hidden',''); });
  var HID = uf ? 'until-found' : '';
  var stack = [];
  function setGroup(g, open){
    document.querySelectorAll('[data-g="'+g+'"]').forEach(function(el){
      if (el.classList.contains('run')) { if (open) el.removeAttribute('hidden'); else el.setAttribute('hidden', HID); }
      else if (el.classList.contains('row')) {
        el.classList.toggle('is-open', open);
        if (el.hasAttribute('data-row')) { if (open) el.removeAttribute('hidden'); else el.setAttribute('hidden', HID); }
      }
    });
    document.querySelectorAll('[data-toggle="'+g+'"]').forEach(function(b){
      if (b.dataset.bot) { b.hidden = !open; return; }
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
      var t2 = b.querySelector('.tg2'); if (t2) t2.textContent = open ? (String.fromCharCode(8722) + ' hide') : t2.dataset.more;
      var al = b.getAttribute('aria-label') || '';
      b.setAttribute('aria-label', open ? al.replace(/^Show \d+ more entries in/, 'Hide the extra entries in') : (b.dataset.al || al));
    });
    var i = stack.indexOf(g); if (i > -1) stack.splice(i,1); if (open) stack.push(g);
  }
  document.querySelectorAll('.tg[aria-label]').forEach(function(b){ b.dataset.al = b.getAttribute('aria-label'); });
  function topLabel(g){
    var vis = Array.prototype.filter.call(document.querySelectorAll('.tg[data-toggle="'+g+'"]:not([data-bot])'),
      function(b){ return b.offsetParent !== null; });
    return vis[0];
  }
  document.addEventListener('click', function(e){
    var b = e.target.closest('[data-toggle]'); if (!b) return;
    var g = b.dataset.toggle, top = topLabel(g);
    var open = !(top && top.getAttribute('aria-expanded') === 'true');
    if (b.dataset.bot) {                       /* closing from the bottom: bring the label back into view */
      setGroup(g, false);
      if (top) { if (top.getBoundingClientRect().top < 0) top.scrollIntoView({block:'start'}); top.focus({preventScroll:true}); }
      return;
    }
    setGroup(g, open);
  });
  document.addEventListener('keydown', function(e){
    if (e.key !== 'Escape' || !stack.length || document.querySelector('dialog[open]')) return;
    var g = stack[stack.length-1]; setGroup(g, false);
    var top = topLabel(g); if (top) { top.focus({preventScroll:true}); top.scrollIntoView({block:'nearest'}); }
  });
  document.addEventListener('beforematch', function(e){
    var el = e.target.closest('[data-g]'); if (el) setGroup(el.dataset.g, true);
  }, true);
  var all = document.getElementById('allbtn');
  if (all) all.addEventListener('click', function(){
    var y0 = all.getBoundingClientRect().top, open = all.getAttribute('aria-expanded') !== 'true';
    var gs = {}; document.querySelectorAll('[data-toggle]').forEach(function(b){ gs[b.dataset.toggle] = 1; });
    Object.keys(gs).forEach(function(g){ setGroup(g, open); });
    all.setAttribute('aria-expanded', open ? 'true' : 'false');
    all.textContent = open ? 'Hide all' : all.dataset.label;
    window.scrollBy(0, all.getBoundingClientRect().top - y0);
  });
})();

(function(){
  /* person data is loaded once, in the background, from data/people.json */
  if (!document.getElementById('pm')) return;   /* text pages have no person dialog */
  var D = null;
  var ready = fetch('data/people.json').then(function(r){ return r.json(); }).then(function(j){ D = j; return j; });
  var dlg = document.getElementById('pm'), last = null;
  function $(id){ return document.getElementById(id); }
  function show(pid){
    var r = D && D[pid]; if (!r) return false;
    dlg.style.setProperty('--pc', r.c === 'grey' ? 'var(--grey)' : 'var(--' + r.c + ')');
    $('pm-line').innerHTML = r.l;
    $('pm-name').textContent = r.n;
    $('pm-office').innerHTML = r.o || '';
    var pic = $('pm-pic');
    if (r.img) pic.innerHTML = '<img alt="" src="' + r.img + '">';
    else pic.textContent = r.n.replace(/^(St|Pope) /,'').split(' ').slice(0,2).map(function(w){return w[0];}).join('');
    var f = '';
    if (r.t) f += '<dt>In office</dt><dd>' + r.t + '</dd>';
    if (r.life) f += '<dt>Life</dt><dd>' + r.life + '</dd>';
    $('pm-facts').innerHTML = f;
    $('pm-tag').innerHTML = r.tag || ''; $('pm-tag').hidden = !r.tag;
    $('pm-bio').textContent = r.bio || 'Wikipedia has no article for this holder.';
    $('pm-src').innerHTML = r.w ? 'From Wikipedia &middot; <a target="_blank" rel="noopener" href="https://en.wikipedia.org/wiki/' +
      encodeURIComponent(r.w.replace(/ /g,'_')) + '">Read the full article</a>' : '';
    var tr = $('pm-trace');
    if (tr) {
      var none = ['lutheran', 'reformed', 'free', 'grey'].indexOf(r.c) > -1;
      tr.innerHTML = none ? (r.c === 'grey' ? '' : 'Made no claim to succession in office.')
        : '<a href="' + (r.sh || ('line.html?p=' + encodeURIComponent(pid))) + '">Follow the line back &rarr;</a>';
      tr.hidden = r.c === 'grey';
    }
    if (r.ev) {
      $('pm-ev').hidden = false;
      $('pm-evt').innerHTML = '<b>' + r.ev[0] + '</b> &middot; ' + r.ev[1] + ' <a target="_blank" rel="noopener" href="https://en.wikipedia.org/wiki/' +
        encodeURIComponent(r.ev[2].replace(/ /g,'_')) + '">Read about it</a>';
      $('pm-evr').textContent = r.ev[3].charAt(0).toUpperCase() + r.ev[3].slice(1) + '.';
    } else $('pm-ev').hidden = true;
    var pv = $('pm-prev'), nx = $('pm-next');
    pv.hidden = !(r.prev && r.pn); nx.hidden = !(r.next && r.nn);
    if (r.prev) { pv.querySelector('b').textContent = '\u2190 ' + r.pn; pv.dataset.p = r.prev; }
    if (r.next) { nx.querySelector('b').textContent = r.nn + ' \u2192'; nx.dataset.p = r.next; }
    dlg.querySelector('.pm__in').scrollTop = 0;
    return true;
  }
  document.addEventListener('click', function(e){
    var t = e.target.closest('[data-p]');
    if (t && !dlg.contains(t)) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
      e.preventDefault();
      ready.then(function(){
        if (show(t.dataset.p)) { last = t; if (!dlg.open) dlg.showModal(); }
        else if (t.href) window.open(t.href, '_blank', 'noopener');
      }, function(){ if (t.href) window.open(t.href, '_blank', 'noopener'); });
      return;
    }
    if (t && dlg.contains(t)) { e.preventDefault(); show(t.dataset.p); return; }
    if (e.target.closest('[data-close]')) dlg.close();
  });
  dlg.addEventListener('click', function(e){ if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('close', function(){ if (last) last.focus({preventScroll:true}); });
  function fromHash(){
    var m = location.hash.match(/^#p=(.+)$/); if (!m) return;
    var pid = decodeURIComponent(m[1]);
    ready.then(function(){ if (show(pid) && !dlg.open) dlg.showModal(); });
    history.replaceState(null, '', location.pathname + location.search);
  }
  fromHash(); window.addEventListener('hashchange', fromHash);
})();

(function(){
  /* site nav: the Churches menu, the theme switch, and a hairline once the page has scrolled */
  var btn = document.getElementById('menubtn'), panel = document.getElementById('menu');
  function setMenu(open){ if (!btn) return; btn.setAttribute('aria-expanded', open ? 'true' : 'false'); panel.hidden = !open; }
  if (btn) {
    btn.addEventListener('click', function(){ setMenu(panel.hidden); if (!panel.hidden) { var a = panel.querySelector('a'); if (a) a.focus(); } });
    document.addEventListener('click', function(e){ if (!panel.hidden && !e.target.closest('.menu')) setMenu(false); });
    panel.addEventListener('click', function(e){ if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function(e){
      if (e.key === 'Escape' && !panel.hidden) { e.stopImmediatePropagation(); setMenu(false); btn.focus(); }
    }, true);
  }
  var tb = document.getElementById('themebtn'), root = document.documentElement;
  function isDark(){ var t = root.getAttribute('data-theme'); return t ? t === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; }
  function label(){ if (tb) tb.setAttribute('aria-label', isDark() ? 'Switch to light theme' : 'Switch to dark theme'); }
  if (tb) {
    label();
    tb.addEventListener('click', function(){
      var t = isDark() ? 'light' : 'dark'; root.setAttribute('data-theme', t);
      try { localStorage.setItem('theme', t); } catch (e) {}
      label();
    });
  }
  var nav = document.getElementById('nav');
  function stuck(){ if (nav) nav.classList.toggle('nav--stuck', window.scrollY > 4); }
  window.addEventListener('scroll', stuck, {passive:true}); stuck();
})();

(function(){
  /* search: every person on the site, by name, office, line or year in office */
  var dlg = document.getElementById('sx'), btn = document.getElementById('searchbtn');
  if (!dlg || !btn) return;
  var q = document.getElementById('sx-q'), list = document.getElementById('sx-res'), status = document.getElementById('sx-status');
  var hint = status.innerHTML, data = null, rows = [], active = -1, timer = null;
  var ORDER = {anglican:0, catholic:1, orthodox:2};
  function norm(s){ return (s || '').replace(/&[a-z]+;|&#\d+;/g, ' ').replace(/<[^>]+>/g, ' ').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function load(){
    if (data) return Promise.resolve(data);
    return fetch('data/people.json').then(function(r){ return r.json(); }).then(function(j){
      data = Object.keys(j).map(function(pid){
        var r = j[pid];
        return {pid:pid, r:r, name:norm(r.n), rest:norm(r.o + ' ' + r.l + ' ' + (r.c || '')), words:norm(r.n).split(/[\s\-']+/)};
      });
      return data;
    });
  }
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function initials(n){ return n.replace(/^(St|Pope|Saint) /, '').split(/\s+/).slice(0, 2).map(function(w){ return w.charAt(0); }).join(''); }
  function run(){
    var raw = q.value.trim(), text = norm(raw);
    if (!text) { list.innerHTML = ''; status.innerHTML = hint; rows = []; active = -1; return; }
    load().then(function(all){
      var year = null, toks = [];
      text.split(/\s+/).forEach(function(t){ if (/^\d{2,4}$/.test(t) && year === null) year = +t; else if (t) toks.push(t); });
      var hits = [];
      all.forEach(function(p){
        if (year !== null && !(p.r.y || []).some(function(a){ return a[0] <= year && year <= a[1]; })) return;
        var score = 0;
        for (var i = 0; i < toks.length; i++) {
          var t = toks[i], s = 0;
          if (p.name.indexOf(t) === 0) s = 6;
          else if (p.words.some(function(w){ return w.indexOf(t) === 0; })) s = 4;
          else if (p.name.indexOf(t) > -1) s = 2;
          else if (p.rest.indexOf(t) > -1) s = 1;
          if (!s) return;
          score += s;
        }
        hits.push({p:p, s:score});
      });
      hits.sort(function(a, b){
        return (b.s - a.s) || ((ORDER[a.p.r.c] === undefined ? 9 : ORDER[a.p.r.c]) - (ORDER[b.p.r.c] === undefined ? 9 : ORDER[b.p.r.c])) ||
               (((a.p.r.y || [[0]])[0][0]) - ((b.p.r.y || [[0]])[0][0]));
      });
      rows = hits.slice(0, 40);
      list.innerHTML = rows.map(function(h, i){
        var r = h.p.r, c = r.c === 'grey' ? 'grey' : r.c;
        var pic = r.img ? '<img src="' + esc(r.img) + '" alt="" loading="lazy">' : esc(initials(r.n));
        var meta = [r.o || r.l, r.t].filter(Boolean).join(' &middot; ');
        return '<li role="presentation"><a id="sx-' + i + '" role="option" aria-selected="false" style="--c:var(--' + c + ')" data-p="' + esc(h.p.pid) + '" href="' +
          esc(r.pg || 'index.html') + '#p=' + encodeURIComponent(h.p.pid) + '"><span class="sx__pic" aria-hidden="true">' + pic + '</span>' +
          '<span class="sx__t"><span class="sx__n">' + esc(r.n) + '</span><span class="sx__m">' + meta + '</span></span></a>' +
          (['lutheran', 'reformed', 'free', 'grey'].indexOf(r.c) > -1 ? '' : '<a class="sx__line" href="' + esc(r.sh || ('line.html?p=' + encodeURIComponent(h.p.pid))) + '" aria-label="Follow the line back from ' + esc(r.n) + '">Line</a>') + '</li>';
      }).join('');
      var who = year !== null ? ' in office in ' + year : '';
      status.textContent = hits.length ? (hits.length > rows.length ? 'Showing ' + rows.length + ' of ' + hits.length + ' people' + who : hits.length + (hits.length === 1 ? ' person' : ' people') + who)
                                       : 'No one found' + who + '.';
      setActive(rows.length ? 0 : -1);
    });
  }
  function setActive(i){
    var items = list.querySelectorAll('a[role=option]');
    if (active > -1 && items[active]) items[active].setAttribute('aria-selected', 'false');
    active = i;
    if (i > -1 && items[i]) { items[i].setAttribute('aria-selected', 'true'); items[i].scrollIntoView({block:'nearest'}); q.setAttribute('aria-activedescendant', items[i].id); }
    else q.removeAttribute('aria-activedescendant');
  }
  function open(){ if (dlg.open) return; dlg.showModal(); q.focus(); q.select(); load(); }
  btn.addEventListener('click', open);
  q.addEventListener('input', function(){ clearTimeout(timer); timer = setTimeout(run, 60); });
  q.addEventListener('keydown', function(e){
    var n = list.querySelectorAll('a[role=option]').length;
    if (e.key === 'ArrowDown') { e.preventDefault(); if (n) setActive((active + 1) % n); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); if (n) setActive((active - 1 + n) % n); }
    else if (e.key === 'Enter') { e.preventDefault(); var a = list.querySelectorAll('a[role=option]')[active]; if (a) a.click(); }
  });
  list.addEventListener('mousemove', function(e){
    var a = e.target.closest('a[role=option]'); if (!a) return;
    var i = Array.prototype.indexOf.call(list.querySelectorAll('a[role=option]'), a); if (i !== active) setActive(i);
  });
  /* choosing a result: on a chart page the person dialog opens here (its own click handler picks up data-p); elsewhere the link goes to their page */
  list.addEventListener('click', function(e){
    var a = e.target.closest('a[role=option]'); if (!a) return;
    if (!document.getElementById('pm')) return;
    dlg.close();
  });
  dlg.addEventListener('click', function(e){ if (e.target === dlg || e.target.closest('[data-sx-close]')) dlg.close(); });
  document.addEventListener('keydown', function(e){
    var typing = /INPUT|TEXTAREA|SELECT/.test((e.target.tagName || '')) || e.target.isContentEditable;
    if (((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') || (e.key === '/' && !typing && !document.querySelector('dialog[open]'))) { e.preventDefault(); open(); }
  });
})();

(function(){
  /* Follow the line back: one person's office, predecessor by predecessor, joining older lines only at recorded acts */
  var root = document.getElementById('trace');
  if (!root && !document.querySelector('main.trace')) return;
  root = root || document.querySelector('main.trace');
  var qs = new URLSearchParams(location.search);
  var start = root.getAttribute('data-trace') || qs.get('p');
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function ord(n){ var s = ['th','st','nd','rd'], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); }
  function initials(n){ return n.replace(/^(St|Pope|Saint) /, '').split(/\s+/).slice(0, 2).map(function(w){ return w.charAt(0); }).join(''); }
  function hue(c){ return 'var(--' + (c === 'grey' ? 'grey' : c) + ')'; }

  Promise.all([fetch('data/people.json').then(function(r){ return r.json(); }), fetch('data/trace.json').then(function(r){ return r.json(); })])
    .then(function(res){ draw(res[0], res[1]); }, function(){ root.innerHTML = '<p class="tr__empty">The line could not be loaded.</p>'; });

  function plainText(s){ return String(s || '').replace(/<[^>]+>|&[a-z]+;/g, ' ').replace(/[^a-z ]/gi, '').replace(/\s+/g, ' ').trim().toLowerCase(); }
  /* family-page cards fall back to the office as their one-liner; don't repeat it under every name */
  function sameAsOffice(r){ var t = plainText(r.tag), o = plainText(r.o) + ' ' + plainText(r.l); return !t || o.indexOf(t) > -1; }
  function yearOf(r){ return r.y && r.y.length ? r.y[0][0] : 30; }
  function endOf(r){ return r.y && r.y.length ? r.y[r.y.length - 1][1] : 60; }

  function chooser(P, T){
    document.title = 'Follow the line back · Lineage of the Church';
    root.innerHTML = '<header class="tr__head"><span class="mast__kicker">Follow the line back</span><h1>Choose someone to follow back</h1>' +
      '<p class="tr__sub">Pick anyone on the chart, or start from a church&rsquo;s current leader. Their office is followed back, predecessor by predecessor, as each church records it.</p>' +
      '<p class="tr__actions"><button type="button" class="tr__btn" id="tr-search">Search for a name</button></p></header>' +
      '<ul class="tr__pick">' + T.current.map(function(pid){
        var r = P[pid]; if (!r) return '';
        var pic = r.img ? '<img src="' + esc(r.img) + '" alt="" loading="lazy">' : esc(initials(r.n));
        return '<li><a href="' + esc(r.sh || ('line.html?p=' + encodeURIComponent(pid))) + '" style="--c:' + hue(r.c) + '"><span class="tr__pic" aria-hidden="true">' + pic +
          '</span><span><b>' + esc(r.n) + '</b><small>' + (r.o || r.l) + '</small></span></a></li>';
      }).join('') + '</ul>';
    var sb = document.getElementById('tr-search'), nb = document.getElementById('searchbtn');
    if (sb && nb) sb.addEventListener('click', function(){ nb.click(); });
  }

  function draw(P, T){
    if (!start) return chooser(P, T);
    var pid = T.alias[start] || start, me = P[pid];
    if (!me) return chooser(P, T);
    var name = me.n;
    document.title = 'The line before ' + name + ' · Lineage of the Church';
    if (T.none.indexOf(me.c) > -1) {
      root.innerHTML = '<header class="tr__head"><span class="mast__kicker">Follow the line back</span><h1>' + esc(name) + '</h1>' +
        '<p class="tr__sub">' + (me.c === 'grey' ? 'The churches trace themselves to him.' : esc(name) + ' made no claim to succession in office, so there is no line to follow back.') + '</p>' +
        '<p class="tr__actions"><a class="tr__btn" href="line.html">Choose someone else</a></p></header>';
      return;
    }
    /* walk: predecessors in office, then across a recorded join into the older line */
    var secs = [], cur = pid;
    for (var guard = 0; guard < 8 && cur; guard++) {
      var hs = [], p = cur, seen = {};
      while (p && P[p] && !seen[p]) { seen[p] = 1; hs.push(p); p = P[p].prev; }
      hs.reverse();
      var line = P[cur].c, meta = T.lines[line] || {}, j = meta.join && P[meta.join[0]] ? meta.join : null;
      secs.unshift({line: line, meta: meta, holders: hs, join: j});
      cur = j ? j[0] : null;
    }
    var total = secs.reduce(function(n, s){ return n + s.holders.length; }, 0) - 1;
    var first = P[secs[0].holders[0]], firstYear = yearOf(first);
    var churches = secs.length;

    /* which holders get a card: the first of each section, its last (where a join leaves it), featured holders, the person */
    var html = [];
    html.push('<header class="tr__head"><span class="mast__kicker">Follow the line back</span>' +
      '<h1>The line before ' + esc(name) + '</h1>' +
      '<p class="tr__sub">' + (me.o || me.l) + '. Followed back through ' + total + ' predecessor' + (total === 1 ? '' : 's') +
      (churches > 1 ? ' in ' + churches + ' churches&rsquo; lists' : '') + ', from ' + (firstYear < 100 ? 'the 1st century' : firstYear) + ' to ' + yearOf(me) + ', as each church records it.</p>' +
      '<p class="tr__actions"><a class="tr__btn" href="#tr-you">Jump to ' + esc(name) + ' &darr;</a>' +
      '<button type="button" class="tr__btn tr__btn--ghost" id="tr-share">Share</button><span class="tr__status" id="tr-status" role="status"></span></p>' +
      '<p class="tr__key"><span class="k k--rec">Recorded</span><span class="k k--early">Early lists or tradition</span><span class="k k--mark">Division</span></p></header>');
    html.push('<ol class="tr__line">');
    var oldest = secs[0].meta;
    html.push('<li class="tr__begin" style="--c:' + hue(secs[0].line) + '"><p>' + (oldest.begins || '') + '</p>' +
      (oldest.gap ? '<p class="tr__gap">' + oldest.gap + '</p>' : '') + '<p class="tr__jesus">The churches trace themselves to Jesus of Nazareth.</p></li>');

    secs.forEach(function(sec, si){
      var meta = sec.meta, hs = sec.holders, c = hue(sec.line);
      if (si > 0) {
        var prevSec = secs[si - 1], jy = sec.join ? (sec.join[3] || sec.join[1]) : '';
        html.push('<li class="tr__cross" style="--c0:' + hue(prevSec.line) + ';--c:' + c + '"><span class="tr__y">' + jy + '</span>' +
          '<h2>From ' + esc(prevSec.meta.church || '') + ' to ' + esc(meta.church || '') + '</h2><p>' + (sec.join ? sec.join[2] : '') + '</p>' +
          (meta.gap ? '<p class="tr__gap">' + meta.gap + '</p>' : '') + '</li>');
      }
      var endY = si < secs.length - 1 ? (secs[si + 1].join ? secs[si + 1].join[1] : endOf(P[hs[hs.length - 1]])) : yearOf(me);
      var startY = si > 0 && sec.join ? sec.join[1] - 10 : yearOf(P[hs[0]]);
      var marks = (meta.markers || []).filter(function(m){ return m[0] >= startY && m[0] <= endY; }).slice();
      var run = [];
      function certainty(r, i){
        var y = yearOf(r);
        if (i === 0 && si === 0 && y < 100) return 'trad';
        if (meta.early && y < meta.early) return 'early';
        return 'rec';
      }
      function flush(nextYear){
        if (!run.length) return;
        var ys = run.map(function(id){ return yearOf(P[id]); });
        var a = ys[0], b = endOf(P[run[run.length - 1]]);
        var span = Math.max(1, (nextYear || b) - (run.prevYear || a));
        var h = Math.max(30, Math.min(240, span * 0.45));
        var soft = run.every(function(id){ return run.cert[id] !== 'rec'; });
        var ticks = run.map(function(id, k){ var t = (ys[k] - (run.prevYear || a)) / span; return '<i style="top:' + Math.max(0, Math.min(100, t * 100)).toFixed(1) + '%"></i>'; }).join('');
        var label = run.length + ' ' + (run.length === 1 ? (meta.office || '').replace(/s( |$)/, '$1') : meta.office);
        html.push('<li class="tr__run' + (soft ? ' is-soft' : '') + '" style="--c:' + c + '"><div class="tr__ticks" style="height:' + h.toFixed(0) + 'px" aria-hidden="true">' + ticks + '</div>' +
          '<div class="tr__runtxt"><button type="button" class="tr__fold" aria-expanded="false">' + label + ' &middot; ' + a + '&ndash;' + b + '</button>' +
          '<ol class="tr__names" hidden>' + run.map(function(id){ var r = P[id];
            return '<li><button type="button" data-p="' + esc(id) + '">' + esc(r.n) + '</button> <span>' + (r.t || '') + '</span></li>'; }).join('') + '</ol></div></li>');
        run = [];
      }
      run.cert = {};
      hs.forEach(function(id, i){
        var r = P[id], y = yearOf(r), cert = certainty(r, i);
        while (marks.length && marks[0][0] <= y) { flush(marks[0][0]); var m = marks.shift(); html.push('<li class="tr__mark" style="--c:' + c + '"><span class="tr__y">' + m[0] + '</span><p>' + m[1] + '</p></li>'); run.cert = {}; }
        var isYou = id === pid, named = isYou || i === 0 || i === hs.length - 1 || !!r.tag;
        if (!named) { if (!run.length) run.prevYear = y; run.cert[id] = cert; run.push(id); return; }
        flush(y); run.cert = {};
        var pic = r.img ? '<img src="' + esc(r.img) + '" alt="" loading="lazy">' : '<span>' + esc(initials(r.n)) + '</span>';
        var label = cert === 'trad' ? 'by tradition' : (cert === 'early' ? 'early lists' : '');
        html.push('<li class="tr__card is-' + cert + (isYou ? ' tr__card--you' : '') + '"' + (isYou ? ' id="tr-you" tabindex="-1"' : '') + ' style="--c:' + c + '">' +
          '<span class="tr__pic" aria-hidden="true">' + pic + '</span><div class="tr__txt">' +
          '<button type="button" class="tr__nm" data-p="' + esc(id) + '">' + esc(r.n) + '</button>' +
          '<span class="tr__mt">' + (r.t || (r.y && r.y.length ? '' : '1st century')) + (label ? ' &middot; <i>' + label + '</i>' : '') + '</span>' +
          (isYou ? '<span class="tr__of">' + (r.o || '') + '</span>' : (r.tag && !sameAsOffice(r) ? '<span class="tr__bio">' + r.tag + '</span>' : '')) + '</div></li>');
      });
      flush(null);
      marks.forEach(function(m){ html.push('<li class="tr__mark" style="--c:' + c + '"><span class="tr__y">' + m[0] + '</span><p>' + m[1] + '</p></li>'); });
    });
    html.push('</ol><p class="tr__foot">Each step follows succession in office, as the church concerned lists it. Joins between churches are recorded historical acts. ' +
      'This is a timeline, not a statement about the validity of anyone&rsquo;s orders. <a href="about.html">About the sources</a>.</p>');
    root.innerHTML = html.join('');

    root.addEventListener('click', function(e){
      var f = e.target.closest('.tr__fold'); if (!f) return;
      var open = f.getAttribute('aria-expanded') !== 'true', li = f.closest('.tr__run');
      f.setAttribute('aria-expanded', open ? 'true' : 'false');
      li.querySelector('.tr__names').hidden = !open; li.classList.toggle('is-open', open);
    });
    var share = document.getElementById('tr-share'), status = document.getElementById('tr-status');
    share.addEventListener('click', function(){
      var url = new URL(me.sh || ('line.html?p=' + encodeURIComponent(pid)), location.href).href, title = 'The line before ' + name;
      if (navigator.share) { navigator.share({title: title, url: url}).catch(function(){}); return; }
      (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(function(){ status.textContent = 'Link copied'; },
        function(){ status.textContent = url; });
      setTimeout(function(){ status.textContent = ''; }, 4000);
    });
    if (location.hash === '#tr-you') { var you = document.getElementById('tr-you'); if (you) you.scrollIntoView({block:'center'}); }
  }
})();

(function(){
  /* The register: all leaders on the site, list by list, newest first, filling the intro.
     Lists are cut into chunks and dealt to whichever column holds the fewest characters, so every column carries several
     lines and fills evenly at one font size. If even the smallest size overflows, every list is trimmed by the same share. */
  var hero = document.querySelector('.hero'), wall = hero && hero.querySelector('.wall');
  if (!wall) return;
  var cols = wall.querySelector('.wall__cols'), block = hero.querySelector('.hero__in'), html = document.documentElement;
  var MIN = 5, MAX = 13, data = null, built = '';
  function colCount(w){ return w < 600 ? 3 : w < 1000 ? 5 : w < 1440 ? 7 : w < 1920 ? 9 : 11; }
  function nb(s){ return s.replace(/ /g, ' '); }
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function build(n, share){
    var lists = data.map(function(L){
      var keep = Math.max(1, Math.round(L.names.length * share)), names = L.names.slice(0, keep);
      if (keep < L.names.length) names.push('… and ' + (L.names.length - keep) + ' earlier');
      return {L: L, names: names};
    });
    var total = 0; lists.forEach(function(x){ x.names.forEach(function(nm){ total += nm.length + 3; }); total += 30; });
    var cap = total / (n * 4), chunks = [];
    lists.forEach(function(x){
      var cur = [], chars = 30, first = true;
      x.names.forEach(function(nm){
        if (chars + nm.length + 3 > cap && cur.length) { chunks.push({x: x, names: cur, first: first, chars: chars}); cur = []; chars = 12; first = false; }
        cur.push(nm); chars += nm.length + 3;
      });
      if (cur.length) chunks.push({x: x, names: cur, first: first, chars: chars});
    });
    var load = [], out = [];
    for (var i = 0; i < n; i++) { load.push(0); out.push([]); }
    chunks.forEach(function(ch){
      var k = 0; for (var i = 1; i < n; i++) if (load[i] < load[k]) k = i;
      load[k] += ch.chars; out[k].push(ch);
    });
    cols.style.setProperty('--n', n);
    cols.innerHTML = out.map(function(list){
      return '<div class="wall__col">' + list.map(function(ch){
        var L = ch.x.L;
        return '<p class="wall__chunk" data-line="' + L.c + '" style="--c:var(--' + L.c + ')"><b>' + (ch.first ? esc(L.label) + ' · ' + L.names.length : '<i>' + esc(L.short) + ', continued</i>') + '</b>' +
          ch.names.map(function(nm){ return esc(nb(nm)); }).join(' · ') + '</p>';
      }).join('') + '</div>';
    }).join('');
  }
  function overflows(){
    var cs = cols.children;
    for (var i = 0; i < cs.length; i++) if (cs[i].scrollHeight > cs[i].clientHeight + 1) return true;
    return false;
  }
  function fit(){
    var n = colCount(window.innerWidth), share = 1;
    for (var attempt = 0; attempt < 8; attempt++) {
      build(n, share);
      var lo = MIN, hi = MAX, best = null;
      for (var i = 0; i < 8; i++) {
        var mid = (lo + hi) / 2; cols.style.setProperty('--fs', mid + 'px');
        if (!overflows()) { best = mid; lo = mid; } else hi = mid;
      }
      if (best !== null) { cols.style.setProperty('--fs', best.toFixed(2) + 'px'); break; }
      cols.style.setProperty('--fs', MIN + 'px');
      share *= 0.88;
    }
    /* clear the text block: its box plus 32px, feathered over the mask's --f */
    var w = cols.getBoundingClientRect(), b = block.getBoundingClientRect(), pad = 32;
    cols.style.setProperty('--x0', Math.max(0, b.left - w.left - pad) + 'px');
    cols.style.setProperty('--x1', Math.min(w.width, b.right - w.left + pad) + 'px');
    cols.style.setProperty('--y0', Math.max(0, b.top - w.top - pad) + 'px');
    cols.style.setProperty('--y1', Math.min(w.height, b.bottom - w.top + pad) + 'px');
    built = n + 'x' + window.innerHeight;
  }
  function ready(){
    wall.classList.add('is-ready');
    if (!html.classList.contains('hero-play')) { hero.classList.add('is-settled'); return; }
    try { sessionStorage.setItem('heroSeen', '1'); } catch (e) {}
    hero.classList.add('is-entering');
    setTimeout(function(){ hero.classList.add('is-settled'); }, 1300);
  }
  var fonts = document.fonts && document.fonts.ready ? Promise.race([document.fonts.ready, new Promise(function(r){ setTimeout(r, 600); })]) : Promise.resolve();
  Promise.all([fetch('data/wall.json').then(function(r){ return r.json(); }), fonts]).then(function(res){
    data = res[0]; fit(); ready();
  }, function(){ ready(); });
  var t = null;
  window.addEventListener('resize', function(){
    if (!data) return; clearTimeout(t);
    t = setTimeout(function(){ if (built !== colCount(window.innerWidth) + 'x' + window.innerHeight) fit(); else fit(); }, 150);
  });
  /* hovering a list lights every chunk of that line */
  cols.addEventListener('mouseover', function(e){
    var ch = e.target.closest('.wall__chunk'), line = ch && ch.getAttribute('data-line');
    Array.prototype.forEach.call(cols.querySelectorAll('.wall__chunk'), function(el){ el.classList.toggle('is-lit', !!line && el.getAttribute('data-line') === line); });
  });
  cols.addEventListener('mouseleave', function(){ Array.prototype.forEach.call(cols.querySelectorAll('.is-lit'), function(el){ el.classList.remove('is-lit'); }); });
})();
