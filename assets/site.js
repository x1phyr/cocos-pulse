(function () {
  // Mark active nav from data-nav on <body>
  var current = document.body && document.body.getAttribute("data-nav");
  if (current) {
    document.querySelectorAll(".topnav-links a[data-section]").forEach(function (a) {
      if (a.getAttribute("data-section") === current) {
        a.classList.add("is-active");
      }
    });
  }

  // Ensure ticker has duplicated content for seamless loop if only one set present
  document.querySelectorAll(".ticker-track").forEach(function (track) {
    if (track.dataset.cloned === "1") return;
    var kids = Array.prototype.slice.call(track.children);
    if (kids.length === 0) return;
    // If content already duplicated in markup, skip; else clone once
    var half = Math.floor(kids.length / 2);
    if (half > 0) {
      var first = kids.slice(0, half).map(function (n) { return n.textContent; }).join("|");
      var second = kids.slice(half).map(function (n) { return n.textContent; }).join("|");
      if (first === second) {
        track.dataset.cloned = "1";
        return;
      }
    }
    kids.forEach(function (node) {
      track.appendChild(node.cloneNode(true));
    });
    track.dataset.cloned = "1";
  });
})();
