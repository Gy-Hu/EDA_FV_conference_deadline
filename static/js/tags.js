(function () {
  'use strict';
  var model = window.ConferenceTagModel;
  var definitions = JSON.parse(document.querySelector('.conf-container').dataset.tagDefinitions);
  var cards = Array.from(document.querySelectorAll('.conf')).map(function (node) {
    return { node: node, labels: JSON.parse(node.dataset.conferenceLabels) || {} };
  });

  function element(name, className, text) {
    var node = document.createElement(name);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function chip(definition, entry) {
    var source = typeof entry.source === 'string' && /^https?:\/\//i.test(entry.source) ? entry.source : null;
    var badge = element(source ? 'a' : 'span', 'tag-chip tag-color-' + model.color(definition, entry), model.text(definition, entry));
    var palette = model.palette(entry.tone);
    if (palette) {
      badge.style.setProperty('--tag-bg', palette.background);
      badge.style.setProperty('--tag-ink', palette.ink);
      badge.style.setProperty('--tag-border', palette.border);
    }
    var detail = [definition.description];
    if (entry.category_name) detail.push('Submission category: ' + entry.category_name);
    if (entry.note) detail.push(entry.note);
    if (source) {
      badge.href = source;
      badge.target = '_blank';
      badge.rel = 'noopener noreferrer';
      detail.push('View source');
    }
    badge.title = detail.join('\n');
    badge.setAttribute('aria-label', badge.textContent + '. ' + detail.join(' '));
    return badge;
  }
  cards.forEach(function (card) {
    var container = card.node.querySelector('.conference-tags');
    definitions.forEach(function (definition) {
      var entry = model.normalize(definition, card.labels[definition.key]);
      if (!entry || (definition.kind === 'boolean' && !entry.value)) return;
      container.appendChild(chip(definition, entry));
    });
    if (container.childElementCount) container.hidden = false;
    else container.remove();
  });
})();
