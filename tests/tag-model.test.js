const test = require('node:test');
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const path = require('node:path');
const model = require('../static/js/tag-model');
const definitions = JSON.parse(execFileSync('ruby', ['-ryaml', '-rjson', '-e', 'puts YAML.load_file(ARGV[0]).to_json', path.join(__dirname, '../_data/tag_definitions.yml')], {encoding:'utf8'}));
const field = key => definitions.find(def => def.key === key);

test('missing or raw numeric data never becomes a public badge', () => {
  for (const key of ['registration_fee','submissions','acceptance_rate']) {
    for (const entry of [null, undefined, {}, {value:0}, {value:350}, {tone:'invalid'}, {tone:'heat-21'}, {tone:'heat--1'}]) {
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
    assert.equal(model.normalize(field(key),{value:true,proceedings:true}),null);
    assert.equal(model.normalize(field(key),{value:true,proceedings:true,proceedings_scope:'companion',direct_submission:true}),null);
    assert.equal(model.normalize(field(key),{value:true,proceedings:true,proceedings_scope:'main',direct_submission:true,submission_type:'tool_paper'}).value,true);
  }
  assert.equal(model.normalize(field('short_paper'),{value:true,proceedings:true,proceedings_scope:'main',direct_submission:false}),null);
  assert.ok(model.normalize(field('short_paper'),{value:true,proceedings:true,proceedings_scope:'companion',scope_exception_approved:true,direct_submission:true}));
  assert.equal(model.text(field('short_paper'),{proceedings_scope:'companion',year:2027}), 'Short paper · Companion · 2027');
  assert.equal(model.normalize(field('short_paper'),{value:true,proceedings:true,proceedings_scope:'unknown',scope_exception_approved:true,direct_submission:true}),null);
});
test('tool-related regular research is not a Tool paper category', () => {
  const proof = {value:true,proceedings:true,proceedings_scope:'main'};
  assert.equal(model.normalize(field('tool_paper'), proof), null);
  assert.equal(model.normalize(field('tool_paper'), {...proof,submission_type:'regular_research'}), null);
  for (const submission_type of ['tool_paper','system_description','demo_paper','competition_tool_paper']) {
    assert.ok(model.normalize(field('tool_paper'), {...proof,submission_type}));
  }
});
test('compact regular papers qualify at the layout-specific page limit', () => {
  const proof = {value:true,proceedings:true,proceedings_scope:'main',direct_submission:true,short_basis:'compact_format'};
  for (const [page_layout, limit] of [['two_column',4],['one_column',8]]) {
    assert.ok(model.normalize(field('short_paper'), {...proof,page_layout,content_page_limit:limit}));
    for (const content_page_limit of [0,limit+1,2.5,'4',null]) {
      assert.equal(model.normalize(field('short_paper'), {...proof,page_layout,content_page_limit}),null);
    }
  }
  assert.equal(model.normalize(field('short_paper'), {...proof,page_layout:'unknown',content_page_limit:4}),null);
  const workshop = {...proof,page_layout:'two_column',content_page_limit:4,proceedings_scope:'workshop'};
  assert.equal(model.normalize(field('short_paper'),workshop),null);
  assert.ok(model.normalize(field('short_paper'),{...workshop,scope_exception_approved:true}));
});
test('approved past-edition evidence uses an ordinary badge without claiming the target year', () => {
  const entry = {value:true,proceedings:true,proceedings_scope:'conference',scope_exception_approved:true,submission_type:'demo_paper',year:2026,target_year:2027,reference_only:true};
  assert.equal(model.normalize(field('tool_paper'),entry),null);
  entry.reference_exception_approved = true;
  assert.ok(model.normalize(field('tool_paper'),entry));
  assert.equal(model.text(field('tool_paper'),entry),'Tool paper · Proceedings');
  assert.equal(model.normalize(field('tool_paper'),{...entry,target_year:2026}),null);
});
test('acceptance colors distinguish twenties from forty without rendering values', () => {
  assert.ok(model.normalize(field('acceptance_rate'), {tone:'heat-16'}));
  assert.notDeepEqual(model.palette('heat-16'),model.palette('heat-12'));
  assert.equal(model.palette('heat-21'),null);
  assert.equal(model.text(field('acceptance_rate'),{tone:'heat-16',year:2026}), 'Acceptance Rate · 2026');
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
