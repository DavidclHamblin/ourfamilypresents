/* Our Family Presents: sign-up form and small page touches. */
(function () {
  "use strict";
  var C = window.OFP || {};
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  // "Tell me when it opens" ticks that brand in the sign-up form.
  document.addEventListener("click", function (e) {
    var a = e.target.closest("[data-brand]"); if (!a) return;
    var box = $('.signup input[data-key="' + a.dataset.brand + '"]'); if (box) box.checked = true;
    setTimeout(function () { var em = $("#n-email"); if (em) em.focus({ preventScroll: true }); }, 400);
  });

  $$("form[data-signup]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var msg = $(".form-msg", form);
      var email = (form.email.value || "").trim();
      var brands = $$('input[name="brands"]:checked', form).map(function (x) { return x.value; });
      if (!/^\S+@\S+\.\S+$/.test(email)) { msg.textContent = "Please enter an email address like name@example.com."; return; }
      if (!brands.length) { msg.textContent = "Please tick at least one brand."; return; }
      if (form._honey.value) return;
      var btn = $("button[type=submit]", form); btn.disabled = true; msg.textContent = "Sending…";
      var body = { _subject: "Our Family Presents launch news: " + brands.join(", "), _template: "table", _replyto: email,
        email: email, brands: brands.join(", "), site: "ourfamilypresents.com", form: "launch-news" };
      fetch(C.form, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(body) })
        .then(function (r) { return r.ok ? r.json().then(function (j) { return String(j.success) === "true"; }, function () { return true; }) : false; })
        .catch(function () { return false; })
        .then(function (ok) {
          btn.disabled = false;
          msg.textContent = ok ? "Thank you. We'll email you when they open." : "Sorry, that didn't go through. Please try again, or email " + C.email + ".";
          if (ok) form.email.value = "";
        });
    });
  });

  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
