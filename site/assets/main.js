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

  // Enquiry form. The live site will send this to e-mail through a form
  // service (see README). In the demo we show what would be sent.
  var form = document.getElementById('poptavka');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var d = new FormData(form);
      var lines = [
        'Jméno: ' + (d.get('jmeno') || ''),
        'Telefon: ' + (d.get('telefon') || ''),
        'E-mail: ' + (d.get('email') || '—'),
        'Služba: ' + (d.get('sluzba') || ''),
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
