#!/usr/bin/env python3
"""Render private numeric audit and publish only color buckets / verified labels."""
import json, html, math, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.local-research'
NUMERIC = {'registration_fee', 'submissions', 'acceptance_rate'}
NAMES = {'registration_fee':'注册费','submissions':'投稿量','acceptance_rate':'接收率'}
COLORS = ['green','lime','amber','orange','red']
def metric_tone(value, scale):
    if not scale: return 'slate'
    ratio=max(0,min(1,(value-scale['min'])/(scale['max']-scale['min'])))
    if scale.get('reverse', False): ratio=1-ratio
    if scale.get('bands') == 21:
        # Quantize before publishing: the original value remains private.
        return 'heat-' + str(math.floor(ratio * 20 + 0.5))
    return COLORS[min(4,int(ratio*5))]
def yaml_json(path):
    return json.loads(subprocess.check_output(['ruby','-ryaml','-rjson','-e','puts YAML.load_file(ARGV[0]).to_json',str(path)],text=True,stderr=subprocess.DEVNULL))
definitions = {d['key']:d for d in yaml_json(ROOT/'_data/tag_definitions.yml')}
ledger = json.loads((PRIVATE/'ledger.json').read_text())
source = ROOT/'_data/conferences.yml'
text = source.read_text()
blocks = re.split(r'(?=^- name:)',text,flags=re.M)
public = {}
for conf in ledger['conferences']:
    # Numerical fields can only be published from verified private metrics.
    labels = {key: entry for key, entry in conf['labels'].items() if key not in NUMERIC}
    for key, metric in conf['metrics'].items():
        if key not in NUMERIC or metric.get('status') != 'verified': continue
        value = metric['value']
        assert isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value >= 0
        assert metric.get('source','').startswith(('https://','http://'))
        definition=definitions[key]
        if key=='registration_fee':
            assert metric.get('audience')=='regular_author'
            scale=definition['scales'].get(metric['currency'])
        else:scale=definition['scale']
        if key=='acceptance_rate':assert value<=100
        if key=='submissions':assert value==int(value)
        tone=metric_tone(value, scale)
        # Do not publish metric.value, currency, notes, counts, or calculations.
        labels[key]={'tone':tone,'year':metric['year'],'source':metric['source']}
    for key,entry in labels.items():
        assert key in definitions
        assert entry.get('source','').startswith(('https://','http://')), (conf['name'],key)
        if key in ('tool_paper', 'short_paper'):
            scope_ok=entry.get('proceedings_scope') == 'main' or (entry.get('proceedings_scope') in ('companion','conference','workshop') and entry.get('scope_exception_approved') is True)
            assert entry.get('proceedings') is True and scope_ok, (conf['name'],key)
            if entry.get('year') != conf['edition']:
                assert entry.get('reference_only') is True and entry.get('reference_exception_approved') is True, conf['name']
                assert entry.get('target_year') == conf['edition'] and entry['year'] < conf['edition'], conf['name']
        if key == 'short_paper':
            assert entry.get('direct_submission') is True, conf['name']
            if entry.get('short_basis') == 'compact_format':
                limit=definitions[key]['compact_page_limits'].get(entry.get('page_layout'))
                pages=entry.get('content_page_limit')
                assert limit and type(pages) is int and 1 <= pages <= limit, conf['name']
        if key == 'tool_paper':
            assert entry.get('submission_type') in definitions[key]['allowed_submission_types'], conf['name']
            assert entry.get('category_name'), conf['name']
    public[(conf['name'],conf['edition'])]=labels
for i,block in enumerate(blocks):
    if not block.startswith('- name:'):continue
    name=re.search(r'^- name: (.+)$',block,re.M).group(1).strip('"\'')
    year=int(re.search(r'^  year: (\d+)$',block,re.M).group(1))
    block=re.sub(r'^  labels:.*?(?=^  [a-zA-Z_]+:|\Z)','',block,flags=re.M|re.S)
    labels=public.get((name,year),{})
    if labels:
        serialized=subprocess.check_output(['ruby','-rjson','-ryaml','-e','puts JSON.parse(STDIN.read).to_yaml'],input=json.dumps({'labels':labels}),text=True,stderr=subprocess.DEVNULL)
        serialized=serialized.removeprefix('---\n')
        block=block.rstrip()+'\n'+''.join('  '+line+'\n' for line in serialized.splitlines())+'\n'
    blocks[i]=block
source.write_text(''.join(blocks).rstrip()+'\n')
esc=lambda v:html.escape(str(v))
rows=[]
for c in ledger['conferences']:
    cells=[]
    for key in NAMES:
        m=c['metrics'].get(key)
        if not m:cells.append('<td class="empty">'+esc(c['review'].get(key,'尚未核查'))+'</td>');continue
        value=('≈' if m.get('approximate') else '')+str(m['value']) + (' '+m.get('currency','') if key=='registration_fee' else '%' if key=='acceptance_rate' else ' 篇')
        details=esc(m.get('note',''))
        if m.get('calculation'):details+='<br>计算：'+esc(m['calculation'])
        cells.append(f'<td><b>{esc(value)}</b><small>数据年份：{esc(m["year"])} · {esc(m.get("status"))}</small><p>{details}</p><a href="{esc(m["source"])}">官方来源</a></td>')
    review=''.join('<p><b>'+esc(definitions[k]['label'])+'：</b>'+esc('已核实' if v=='verified' else v)+'</p>' for k,v in c['review'].items()) or '待逐项核查'
    rows.append('<tr><th>'+esc(c['name'])+' '+str(c['edition'])+'</th>'+''.join(cells)+'<td>'+review+'</td></tr>')
doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>会议数据私人核对表</title><style>body{font:14px/1.65 system-ui;margin:32px;color:#24344b}h1{font-size:24px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #dce3ec;padding:12px;vertical-align:top;text-align:left}th{background:#f3f6fa}thead{position:sticky;top:0}td{min-width:180px}small{display:block;color:#64748b}.empty{color:#8792a2}a{color:#2458a5}p{margin:6px 0}</style><h1>会议数据私人核对表</h1><p>仅本地保存，不进入 Git、不进入静态站点。网页上的三项指标仅显示颜色。空白表示未核实或未找到资料，不等于 0。历史数据明确标注年份，费用注明适用条件。</p>'''
complete=ledger.get('work_status',{}).get('complete',False)
status='已逐项核查 '+str(len(ledger['conferences']))+' 条会议记录。' if complete else '调查进行中，尚未完成全量核查。'
doc+='<p><b>'+status+'</b> 未填写项不代表不存在。已记录 '+str(sum(len(c['metrics']) for c in ledger['conferences']))+' 个数值字段（同一会议的多轮投稿可能共用历史统计）。</p><p>核查日期：'+esc(ledger['checked_on'])+'</p><table><thead><tr><th>会议届次</th><th>注册费</th><th>投稿量</th><th>接收率</th><th>核查说明</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></html>'
pending=[]
for c in ledger['conferences']:
    for key,entry in c.get('pending_labels',{}).items():
        links=' '.join('<a href="'+esc(u)+'">来源</a>' for u in entry.get('sources',[]))
        pending.append('<tr><th>'+esc(c['name'])+' '+str(c['edition'])+'</th><td>'+esc(definitions[key]['label'])+'</td><td>'+esc(entry['reason'])+' '+links+'</td></tr>')
if pending:
    section='<h2>待讨论的标签范围</h2><p>这些标签暂不出现在网页上。独立或 companion 论文集不自动意味着质量低；这里仅记录其是否符合所需投稿范围仍待决定。</p><table><thead><tr><th>会议</th><th>标签</th><th>待确认事项</th></tr></thead><tbody>'+''.join(pending)+'</tbody></table>'
    doc=doc.replace('</html>',section+'</html>')
audit=ledger.get('tool_category_audit')
if audit:
    audit_rows=''.join('<tr><th>'+esc(r['name'])+' '+str(r['year'])+'</th><td>'+esc(r['result'])+'</td><td>'+esc(r['reason'])+'</td><td><a href="'+esc(r['source'])+'">官方来源</a></td></tr>' for r in audit['records'])
    audit_doc='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Tool 标签排查</title><style>body{font:15px/1.65 system-ui;margin:28px;color:#24344b}table{border-collapse:collapse;width:100%}td,th{border:1px solid #dce3ec;padding:12px;text-align:left;vertical-align:top}th{background:#f3f6fa}a{color:#2458a5}</style><h1>Tool 标签排查</h1><p>核查日期：'+esc(audit['checked_on'])+'。普通研究轨道接受工具方向，不等于明确的工具论文投稿类别。</p><p>已检查原有 '+str(audit['reviewed_existing_tags'])+' 条 Tool 标签：保留 '+str(audit['retained'])+' 条，撤下 '+str(audit['removed'])+' 条，暂缓 '+str(audit['deferred'])+' 条。计数包含同一会议的多轮投稿记录。</p><table><thead><tr><th>会议</th><th>处理</th><th>依据</th><th>来源</th></tr></thead><tbody>'+audit_rows+'</tbody></table></html>'
    (PRIVATE/'tool-tag-audit.html').write_text(audit_doc)
    doc=doc.replace('</html>','<p><a href="tool-tag-audit.html">查看逐项 Tool 标签排查结果</a></p></html>')
publication_audit=ledger.get('publication_audit')
if publication_audit:
    sections=[]
    for r in publication_audit['records']:
        links=' · '.join('<a href="'+esc(e['url'])+'">'+esc(e['title'])+'</a>' for e in r['sources'])
        sections.append('<section><h2>'+esc(r['name'])+' '+str(r['year'])+' — '+esc(r['category'])+'</h2><p><b>核查状态：</b>'+esc(r['status'])+'</p><p><b>出版物：</b>'+esc(r['publication'])+'</p><p><b>结论：</b>'+esc(r['conclusion'])+'</p><p><b>标签处理：</b>'+esc(r['action'])+'</p><p>'+links+'</p></section>')
    report='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>论文集出版核查结论</title><style>body{max-width:1050px;margin:32px auto;padding:0 20px;font:15px/1.8 system-ui;color:#24344b}h1{font-size:27px}h2{font-size:20px}section{border-top:1px solid #dce3ec;padding:12px 0}a{color:#2458a5}p{margin:8px 0}</style><h1>论文集出版核查结论</h1><p>核查日期：'+esc(publication_audit['checked_on'])+'。同一会议可以有主论文集、companion、workshop分册；分册与否不直接决定学术质量。尚未出版的届次只报告已确认的官方计划，不借用旧届书目信息。</p><p>'+esc(publication_audit['limitations'])+'</p>'+''.join(sections)+'</html>'
    (PRIVATE/'proceedings-review.html').write_text(report)
    doc=doc.replace('</html>','<p><a href="proceedings-review.html">查看论文集出版核查结论</a></p></html>')
(PRIVATE/'conference-metrics-private.html').write_text(doc)
print(json.dumps({'records':len(public),'with_labels':sum(bool(v) for v in public.values()),'public_labels':sum(len(v) for v in public.values()),'private_metrics':sum(len(c['metrics']) for c in ledger['conferences'])}))
