/* Shared pure functions for maintainer-defined conference labels. */
(function (root) {
  'use strict';
  function normalize(definition, entry) {
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)) return null;
    var value = entry.value;
    if (definition.kind === 'boolean') {
      if (typeof value !== 'boolean') return null;
      if (definition.requires_proceedings && value && entry.proceedings !== true) return null;
      if (definition.requires_main_proceedings && value && entry.proceedings_scope !== 'main' && !(['companion','conference','workshop'].indexOf(entry.proceedings_scope) >= 0 && entry.scope_exception_approved === true)) return null;
      if (entry.reference_only && (entry.reference_exception_approved !== true || !Number.isInteger(entry.year) || !Number.isInteger(entry.target_year) || entry.target_year <= entry.year)) return null;
      if (definition.requires_direct_submission && value && entry.direct_submission !== true) return null;
      if (definition.compact_page_limits && value && entry.short_basis === 'compact_format') {
        var limit = definition.compact_page_limits[entry.page_layout];
        if (!limit || !Number.isInteger(entry.content_page_limit) || entry.content_page_limit < 1 || entry.content_page_limit > limit) return null;
      }
      if (definition.allowed_submission_types && value && definition.allowed_submission_types.indexOf(entry.submission_type) < 0) return null;
    } else if (definition.kind === 'number' || definition.kind === 'fee') {
      // Exact values live only in the ignored local research ledger.
      if (['green','lime','amber','orange','red','slate'].indexOf(entry.tone) < 0 && !/^heat-([0-9]|1[0-9]|20)$/.test(entry.tone)) return null;
    } else if (definition.kind === 'ranking') {
      if (definition.options.indexOf(value) < 0) return null;
    } else return null;
    return entry;
  }
  function text(definition, entry) {
    var label = definition.label;
    if (definition.requires_proceedings && entry.proceedings_scope === 'companion') label = label.replace(' · Proceedings', ' · Companion');
    if (definition.kind === 'ranking') label += ' ' + entry.value;
    // Approved historical references use the ordinary badge; provenance stays in the tooltip.
    if (entry.year && !entry.reference_only) label += ' · ' + entry.year;
    return label;
  }
  function color(definition, entry) {
    if (definition.kind === 'ranking') {
      return (definition.colors || {})[entry.value] || 'slate';
    }
    return entry.tone || definition.color || 'slate';
  }
  function palette(tone) {
    if (!/^heat-([0-9]|1[0-9]|20)$/.test(tone)) return null;
    var hue = (20 - Number(tone.slice(5))) * 6.5;
    return { background: 'hsl(' + hue + ', 80%, 94%)', ink: 'hsl(' + hue + ', 75%, 25%)', border: 'hsl(' + hue + ', 65%, 74%)' };
  }
  var api = { normalize: normalize, text: text, color: color, palette: palette };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.ConferenceTagModel = api;
})(typeof window !== 'undefined' ? window : globalThis);
