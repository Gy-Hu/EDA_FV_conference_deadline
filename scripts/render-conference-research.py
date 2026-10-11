#!/usr/bin/env python3
"""Render private numeric audit and publish only color buckets / verified labels."""
import json, html, math, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.local-research'
NUMERIC = {'registration_fee', 'submissions', 'acceptance_rate'}
NAMES = {'registration_fee':'注册费','submissions':'投稿量','acceptance_rate':'接收率'}
COLORS = ['green','lime','amber','orange','red']
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
        tone='slate'
        if scale:
            ratio=max(0,min(1,(value-scale['min'])/(scale['max']-scale['min'])))
            if scale.get('reverse', False): ratio=1-ratio
            tone=COLORS[min(4,int(ratio*5))]
        # Do not publish metric.value, currency, notes, counts, or calculations.
        labels[key]={'tone':tone,'year':metric['year'],'source':metric['source']}
    for key,entry in labels.items():
        assert key in definitions
        assert entry.get('source','').startswith(('https://','http://')), (conf['name'],key)
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
(PRIVATE/'conference-metrics-private.html').write_text(doc)
print(json.dumps({'records':len(public),'with_labels':sum(bool(v) for v in public.values()),'public_labels':sum(len(v) for v in public.values()),'private_metrics':sum(len(c['metrics']) for c in ledger['conferences'])}))
