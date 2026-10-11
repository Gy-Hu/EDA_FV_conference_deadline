/* Shared pure functions for maintainer-defined conference labels. */
(function (root) {
  'use strict';
  function normalize(definition, entry) {
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)) return null;
    var value = entry.value;
    if (definition.kind === 'boolean') {
      if (typeof value !== 'boolean') return null;
      if (definition.requires_proceedings && value && entry.proceedings !== true) return null;
    } else if (definition.kind === 'number' || definition.kind === 'fee') {
      // Exact values live only in the ignored local research ledger.
      if (['green','lime','amber','orange','red','slate'].indexOf(entry.tone) < 0) return null;
    } else if (definition.kind === 'ranking') {
      if (definition.options.indexOf(value) < 0) return null;
    } else return null;
    return entry;
  }
  function text(definition, entry) {
    var label = definition.label;
    if (definition.kind === 'ranking') label += ' ' + entry.value;
    if (entry.year) label += ' · ' + entry.year;
    return label;
  }
  function color(definition, entry) {
    if (definition.kind === 'ranking') {
      return (definition.colors || {})[entry.value] || 'slate';
    }
    return entry.tone || definition.color || 'slate';
  }
  var api = { normalize: normalize, text: text, color: color };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.ConferenceTagModel = api;
})(typeof window !== 'undefined' ? window : globalThis);
