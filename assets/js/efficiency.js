/*
 * Efficiency pages (shortcodes efficiency-era / -roster / -recent / -tickets,
 * and the material filters of efficiency-materials on the stats page).
 *
 * The page is rendered for the default era; everything here is optional
 * enhancement. Picking an era fetches the generated numbers for every era
 * (one JSON file, URL in data-eff-src) and rewrites the cells that carry
 * data-eff-* attributes. No sums are done here -- values come precomputed
 * from tools/build_item_values.py. Also: roster sorting and filters, and the
 * shop packs page's live/ended status.
 *
 * Highlights (recent page only) must match
 * layouts/partials/ica/efficiency/level.html: cells inside
 * data-eff-scale="recent" compare with the recent operators of the same
 * rarity (top quartile = hi, above average = above) and aren't coloured
 * when that rarity has a single recent operator. The roster isn't coloured.
 */
(function () {
  "use strict";

  var STORE_KEY = "ica-efficiency-era";
  var fmt = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
  var selectors = document.querySelectorAll(".eff-era");
  var data = null, pending = null;

  function store(era) {
    try { localStorage.setItem(STORE_KEY, era); } catch (e) { /* private mode etc. */ }
  }
  function stored() {
    try { return localStorage.getItem(STORE_KEY); } catch (e) { return null; }
  }
  function status(text) {
    selectors.forEach(function (s) { s.querySelector(".eff-era__status").textContent = text; });
  }

  function load(src) {
    if (data) return Promise.resolve(data);
    if (!pending) {
      pending = fetch(src).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      }).then(function (d) { data = d; return d; });
      pending.catch(function () { pending = null; });  // allow a retry
    }
    return pending;
  }

  function num(v) { return v === null || v === undefined ? "—" : fmt.format(v); }
  function level(cell, value, average, top) {
    cell.classList.remove("eff-hi", "eff-above");
    if (value === null || value === undefined || !average) return;
    if (value >= top) cell.classList.add("eff-hi");
    else if (value > average) cell.classList.add("eff-above");
  }

  function render(era) {
    var i = data.eras.indexOf(era);
    if (i < 0) return false;
    var ops = data.operators[i];
    document.querySelectorAll("[data-eff-op]").forEach(function (cell) {
      var v = ops.operators[cell.dataset.effOp];
      if (!v) return;
      var col = cell.dataset.effCol;    // "p", a skill index, or "mX"/"mY"/"mD" for modules
      var value = col === "p" ? v.promotion
        : col.charAt(0) === "m" ? (v.modules || {})[col.slice(1)]
        : v.skills[+col];
      var rarity = cell.closest("tr").dataset.rarity;
      var kind = col === "p" ? "promotion" : "mastery";
      cell.textContent = num(value);
      cell.dataset.sort = value === null || value === undefined ? "" : value;
      if (cell.closest('[data-eff-scale="recent"]')) {
        var rs = data.recent[i].rarities[rarity];
        if (rs && rs.count >= 2) level(cell, value, rs[kind + "_average"], rs[kind + "_top_quartile"]);
        else level(cell, null);
      }
    });
    var groups = data.recent[i].groups;
    document.querySelectorAll("[data-eff-group]").forEach(function (cell) {
      var value = groups[+cell.dataset.effGroup][cell.dataset.effStat];
      var signed = cell.hasAttribute("data-eff-signed") && value > 0;
      cell.textContent = (signed ? "+" : "") + num(value);
    });
    // Ticket table: letters / skill packs at the plain average operator
    // (not the packs profile, which drops the cheapest quarter for shop packs).
    var averages = ops.averages || {};
    document.querySelectorAll("[data-eff-avg]").forEach(function (cell) {
      var a = averages[cell.dataset.effAvg];
      cell.textContent = num(a ? a[cell.dataset.effKind] : null);
    });
    var packs = Object.assign({}, data.packs.base, data.packs.eras[i].values);
    document.querySelectorAll("[data-eff-item]").forEach(function (cell) {
      cell.textContent = num(packs[cell.dataset.effItem]);
    });
    return true;
  }

  function choose(era, remember) {
    selectors.forEach(function (s) {
      var input = s.querySelector('input[value="' + era + '"]');
      if (input) input.checked = true;
    });
    if (remember) store(era);
    status("Loading…");
    load(selectors[0].dataset.effSrc).then(function () {
      status(render(era) ? "" : "Unknown era.");
    }).catch(function () {
      status("Couldn’t load the other eras — the numbers shown are for the current shop.");
    });
  }

  if (selectors.length) {
    var defaultEra = selectors[0].dataset.effDefault;
    selectors.forEach(function (s) {
      s.addEventListener("change", function (e) {
        if (e.target.name && e.target.name.indexOf("eff-era") === 0) choose(e.target.value, true);
      });
    });
    var saved = stored();
    if (saved && saved !== defaultEra && selectors[0].querySelector('input[value="' + saved + '"]')) {
      choose(saved, false);
    }
  }

  /* ---- Material tables: operator scope and tier filters ----------------- */
  document.querySelectorAll("[data-eff-mats]").forEach(function (box) {
    var tier = "all";
    function press(attr, btn) {
      box.querySelectorAll("[" + attr + "]").forEach(function (b) {
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
    }
    function filterTiers() {
      box.querySelectorAll("tbody tr").forEach(function (row) {
        row.hidden = tier !== "all" && row.dataset.tier !== tier;
      });
    }
    box.querySelectorAll("[data-eff-scope]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        press("data-eff-scope", btn);
        box.querySelectorAll("[data-eff-scope-body]").forEach(function (body) {
          body.hidden = body.dataset.effScopeBody !== btn.dataset.effScope;
        });
      });
    });
    box.querySelectorAll("[data-eff-tier]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        press("data-eff-tier", btn);
        tier = btn.dataset.effTier;
        filterTiers();
      });
    });

    // Column sorting: every scope's tbody is sorted together, so switching
    // scope keeps the order. Rendered order = sanity, highest first.
    var current = { col: 7, dir: -1 };   // the Sanity column
    function cellValue(row, col, kind) {
      var text = row.cells[col].textContent.trim();
      return kind === "text" ? text.toLowerCase() : +text.replace(/[^0-9.]/g, "");
    }
    box.querySelectorAll("[data-eff-msort]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var col = +btn.dataset.effMsort, kind = btn.dataset.effKind;
        current.dir = current.col === col ? -current.dir : (kind === "text" ? 1 : -1);
        current.col = col;
        box.querySelectorAll("tbody").forEach(function (body) {
          var rows = Array.prototype.slice.call(body.rows);
          rows.sort(function (a, b) {
            var x = cellValue(a, col, kind), y = cellValue(b, col, kind);
            if (x < y) return -current.dir;
            if (x > y) return current.dir;
            return cellValue(a, 0, "text") < cellValue(b, 0, "text") ? -1 : 1;  // ties: by name
          });
          rows.forEach(function (row) { body.appendChild(row); });
        });
        box.querySelectorAll("[data-eff-msort]").forEach(function (b) { b.closest("th").removeAttribute("aria-sort"); });
        btn.closest("th").setAttribute("aria-sort", current.dir === 1 ? "ascending" : "descending");
      });
    });
  });

  /* ---- Shop packs: live / upcoming / ended ------------------------------ */
  // The page is built with each pack's status as of build time, but the site
  // isn't rebuilt the moment a sale starts or ends, and packs often stay on
  // sale after their event. So re-decide from each row's EN sale window
  // (data-pack-start / data-pack-end, from pack_values.json): hide ended
  // packs, hide an event with none left (and its table-of-contents entry),
  // and switch the badge between the page's own Live / Upcoming labels.
  document.querySelectorAll("[data-pack-event]").forEach(function (event) {
    var now = Date.now(), shown = 0, live = false;
    // One <tbody> per pack (its numbers row and contents row).
    event.querySelectorAll("tbody[data-pack-start], tbody[data-pack-end]").forEach(function (row) {
      var start = row.dataset.packStart ? Date.parse(row.dataset.packStart) : null;
      var end = row.dataset.packEnd ? Date.parse(row.dataset.packEnd) : null;
      if (end !== null && end < now) { row.hidden = true; return; }
      if (start !== null && start <= now) live = true;
    });
    event.querySelectorAll("tbody").forEach(function (pack) { if (!pack.hidden) shown++; });
    var heading = event.previousElementSibling;
    if (!shown) {
      event.hidden = true;
      if (heading && /^H[1-6]$/.test(heading.tagName)) {
        heading.hidden = true;
        // Blowfish puts the heading's anchor id on a div inside the heading.
        var anchor = heading.id ? heading : heading.querySelector("[id]");
        if (anchor) {
          // ...and renders the contents twice (sidebar and mobile).
          var href = '[href="#' + anchor.id.replace(/["\\]/g, "\\$&") + '"]';
          document.querySelectorAll("#TableOfContents a" + href + ", #TableOfContentsMobile a" + href).forEach(function (a) {
            a.closest("li").hidden = true;
          });
        }
      }
      return;
    }
    var badge = event.querySelector("[data-pack-badge]");
    if (badge) {
      badge.textContent = live ? event.dataset.labelLive : event.dataset.labelUpcoming;
      badge.classList.toggle("eff-pack-badge--live", live);
    }
  });

  /* ---- Links to a row inside the full list's scroll box (#op-…) --------- */
  // The roster table scrolls in its own box so its header row stays pinned.
  // On a link to one of its rows the browser scrolls both the box and the page,
  // but puts the box's top edge at the very top of the window -- under the
  // site's fixed header. Re-place both: box just below the site header, row
  // just below the pinned header row.
  function showLinkedRow() {
    var id = decodeURIComponent(location.hash.slice(1));
    var row = id && document.getElementById(id);
    var box = row && row.closest(".eff-table-wrap--frozen");
    if (!box) return;
    var head = box.querySelector("thead");
    var site = document.querySelector(".fixed.top-0");
    var siteBottom = site ? site.getBoundingClientRect().bottom : 0;
    box.scrollTop = row.offsetTop - (head ? head.offsetHeight : 0) - 4;
    window.scrollTo({ top: box.getBoundingClientRect().top + window.scrollY - siteBottom - 8, behavior: "instant" });
  }
  window.addEventListener("load", showLinkedRow);
  window.addEventListener("hashchange", showLinkedRow);

  /* ---- Roster: sorting and filters ------------------------------------- */
  document.querySelectorAll(".eff-roster").forEach(function (roster) {
    var tbody = roster.querySelector("tbody");
    var rows = Array.prototype.slice.call(tbody.rows);
    var rarity = "all", cls = "";
    var count = roster.querySelector("[data-eff-count]");

    function filter() {
      var shown = 0;
      rows.forEach(function (row) {
        var ok = (rarity === "all" || row.dataset.rarity === rarity) && (!cls || row.dataset.class === cls);
        row.hidden = !ok;
        if (ok) shown++;
      });
      count.textContent = shown + (shown === 1 ? " operator" : " operators");
    }
    roster.querySelectorAll("[data-eff-rarity]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        rarity = btn.dataset.effRarity;
        roster.querySelectorAll("[data-eff-rarity]").forEach(function (b) {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        filter();
      });
    });
    roster.querySelector("[data-eff-class]").addEventListener("change", function (e) {
      cls = e.target.value;
      filter();
    });

    var current = { key: null, dir: 1 };
    function sortValue(row, key) {
      if (key === "name") return row.dataset.name;
      if (key === "rarity") return row.dataset.key;    // "<9 - rarity>|name": 6★ first, then A-Z
      if (key === "class") return row.dataset.class + "|" + row.dataset.name;
      var cell = row.querySelector('[data-eff-col="' + key + '"]');
      if (!cell) return null;
      var s = cell.dataset.sort !== undefined ? cell.dataset.sort : cell.textContent.replace(/[^0-9.]/g, "");
      return s === "" ? null : +s;
    }
    roster.querySelectorAll("[data-eff-sort]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var key = btn.dataset.effSort;
        var numeric = key !== "name" && key !== "class" && key !== "rarity";
        // Costs sort highest first on the first click; text A-Z.
        current.dir = current.key === key ? -current.dir : (numeric ? -1 : 1);
        current.key = key;
        rows.sort(function (a, b) {
          var x = sortValue(a, key), y = sortValue(b, key);
          if (x === null && y === null) return 0;
          if (x === null) return 1;             // blanks always last
          if (y === null) return -1;
          if (x < y) return -current.dir;
          if (x > y) return current.dir;
          return 0;
        });
        rows.forEach(function (row) { tbody.appendChild(row); });
        roster.querySelectorAll("[data-eff-sort]").forEach(function (b) {
          b.closest("th").removeAttribute("aria-sort");
        });
        btn.closest("th").setAttribute("aria-sort", current.dir === 1 ? "ascending" : "descending");
      });
    });
  });
})();
