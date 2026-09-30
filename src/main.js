(function () {
  // Mobile menu
  var header = document.querySelector('.site-header');
  var btn = document.querySelector('.menu-btn');
  if (header && btn) {
    btn.addEventListener('click', function () {
      var open = header.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Copy phone / e-mail
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var text = b.getAttribute('data-copy');
      var done = function () { var t = b.textContent; b.textContent = 'Zkopírováno'; setTimeout(function () { b.textContent = t; }, 1600); };
      var fallback = function () {
        var target = document.getElementById(b.getAttribute('aria-controls'));
        if (!target) return;
        var r = document.createRange(); r.selectNodeContents(target);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      };
      try { navigator.clipboard.writeText(text).then(done, fallback); } catch (e) { fallback(); }
    });
  });

  // Pre-select service from ?sluzba= or #hash on the contact page
  var sel = document.getElementById('f-sluzba');
  if (sel) {
    var m = (location.hash || '').replace('#', '');
    if (m) { for (var i = 0; i < sel.options.length; i++) { if (sel.options[i].value === m) sel.selectedIndex = i; } }
  }

  // Enquiry form. On the real domain it is sent by poptavka.php (Webglobe PHP mail),
  // anywhere else (demo links) it only shows what would be sent.
  var form = document.getElementById('poptavka');
  if (form) {
    var LIVE = /(^|\.)uklid-pospisil\.cz$/.test(location.hostname);
    var t = document.getElementById('f-t');
    if (t) t.value = Math.floor(Date.now() / 1000);
    var errBox = document.getElementById('poptavka-error');
    var submitBtn = document.getElementById('poptavka-submit');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var d = new FormData(form);
      if (LIVE) {
        errBox.hidden = true;
        submitBtn.disabled = true;
        fetch(form.action, { method: 'POST', body: d, headers: { 'Accept': 'application/json' } })
          .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
          .then(function (res) {
            if (!res.ok) throw new Error(res.message || 'error');
            form.hidden = true;
            var sent = document.getElementById('poptavka-sent');
            sent.hidden = false;
            sent.scrollIntoView({ behavior: 'smooth', block: 'center' });
          })
          .catch(function (err) {
            if (err && err.message && err.message !== 'error' && err.message.indexOf('fetch') < 0) {
              errBox.firstChild.textContent = err.message + ' ';
            }
            errBox.hidden = false;
            submitBtn.disabled = false;
          });
        return;
      }
      var sel = form.querySelector('#f-sluzba');
      var lines = [
        'Jméno: ' + (d.get('jmeno') || ''),
        'Telefon: ' + (d.get('telefon') || ''),
        'E-mail: ' + (d.get('email') || '—'),
        'Služba: ' + (sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].text : ''),
        'Místo úklidu: ' + (d.get('misto') || ''),
        'Termín: ' + (d.get('termin') || 'dle domluvy'),
        '',
        (d.get('zprava') || '')
      ];
      var out = document.getElementById('poptavka-done');
      out.querySelector('pre').textContent = lines.join('\n');
      out.hidden = false;
      form.hidden = true;
      out.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    var again = document.getElementById('poptavka-again');
    if (again) again.addEventListener('click', function () {
      document.getElementById('poptavka-done').hidden = true;
      form.hidden = false;
    });
  }
})();
