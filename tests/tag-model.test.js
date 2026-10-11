const test = require('node:test');
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const path = require('node:path');
const model = require('../static/js/tag-model');
const definitions = JSON.parse(execFileSync('ruby', ['-ryaml', '-rjson', '-e', 'puts YAML.load_file(ARGV[0]).to_json', path.join(__dirname, '../_data/tag_definitions.yml')], {encoding:'utf8'}));
const field = key => definitions.find(def => def.key === key);

test('missing or raw numeric data never becomes a public badge', () => {
  for (const key of ['registration_fee','submissions','acceptance_rate']) {
    for (const entry of [null, undefined, {}, {value:0}, {value:350}, {tone:'invalid'}]) {
      assert.equal(model.normalize(field(key),entry), null);
    }
    assert.equal(model.normalize(field(key),{tone:'green',year:2026}).tone,'green');
  }
});
test('private numbers are never rendered even if passed accidentally', () => {
  assert.equal(model.text(field('registration_fee'), {tone:'green',value:1234,currency:'USD',year:2026}), 'Registration Fee · 2026');
  assert.equal(model.text(field('acceptance_rate'), {tone:'amber',value:25.5,year:2025}), 'Acceptance Rate · 2025');
});
test('paper types require explicit proceedings confirmation', () => {
  for (const key of ['tool_paper','short_paper']) {
    assert.equal(model.normalize(field(key),{value:true}),null);
    assert.equal(model.normalize(field(key),{value:true,proceedings:true}).value,true);
  }
});
test('rankings retain exact verified grades', () => {
  assert.equal(model.normalize(field('ccf_ranking'), {value:'A*'}),null);
  assert.equal(model.text(field('core_ranking'), {value:'A*',year:2026}), 'CORE A* · 2026');
  assert.deepEqual(['A*','A','B','C','Unranked'].map(value => model.color(field('core_ranking'), {value})), ['red','orange','amber','green','slate']);
  assert.deepEqual(['A','B','C','Unranked'].map(value => model.color(field('ccf_ranking'), {value})), ['red','amber','green','slate']);
  assert.equal(model.color(field('registration_fee'), {tone:'green'}), 'green');
});
test('published conference metrics contain only color, year and source', () => {
  const conferences = JSON.parse(execFileSync('ruby', ['-ryaml','-rjson','-e','puts YAML.load_file(ARGV[0]).to_json',path.join(__dirname,'../_data/conferences.yml')],{encoding:'utf8'}));
  for (const conf of conferences) for (const key of ['registration_fee','submissions','acceptance_rate']) {
    const entry = conf.labels?.[key];
    if (!entry) continue;
    assert.deepEqual(Object.keys(entry).sort(),['source','tone','year']);
    assert.ok(model.normalize(field(key),entry));
  }
});
