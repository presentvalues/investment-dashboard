#!/usr/bin/env python3
"""generate_html.py — 从 data.json 生成内嵌数据的自包含 HTML 看板"""

import json, os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "output", "data.json")) as f:
    DATA = json.load(f)

# 时间戳后缀
ts = datetime.now().strftime("%H%M%S")

HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0d1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;padding:20px;max-width:1400px;margin:0 auto}}
h1{{text-align:center;font-size:22px;color:#f0f6fc;margin:10px 0 5px;letter-spacing:1px}}
.subtitle{{text-align:center;font-size:12px;color:#6e7681;margin-bottom:20px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:20px}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px 16px;text-align:center}}
.card-label{{font-size:11px;color:#6e7681;margin-bottom:4px}}
.card-val{{font-size:22px;font-weight:700;color:#f0f6fc}}
.card-val.up{{color:#3fb950}}
.card-val.down{{color:#f85149}}
.card-sub{{font-size:12px;color:#6e7681;margin-top:2px}}
.section{{margin-bottom:24px}}
.section-title{{font-size:15px;font-weight:600;color:#f0f6fc;margin-bottom:10px;padding-left:8px;border-left:3px solid #58a6ff}}
.chart-box{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:8px;margin-bottom:12px}}
.chart{{width:100%;height:360px}}
.chart-sm{{width:100%;height:280px}}
table{{width:100%;border-collapse:collapse;font-size:12px;background:#161b22;border-radius:8px;overflow:hidden}}
th{{background:#21262d;color:#c9d1d9;padding:8px 6px;text-align:center;font-weight:500;border-bottom:1px solid #30363d;white-space:nowrap}}
th:first-child,th:nth-child(2){{text-align:left}}
td{{padding:7px 6px;text-align:center;border-bottom:1px solid #21262d;white-space:nowrap}}
td:first-child,td:nth-child(2){{text-align:left}}
tr:hover{{background:#1c2129}}
.positive{{color:#3fb950}}
.negative{{color:#f85149}}
.footer{{text-align:center;font-size:10px;color:#484f58;margin-top:30px;padding:15px 0;border-top:1px solid #21262d}}
.closed-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
@media(max-width:768px){{.closed-grid{{grid-template-columns:1fr}}}}
.placeholder{{color:#484f58;font-size:20px}}
</style>
</head>
<body>

<h1>{title}</h1>
<p class="subtitle">数据日期: {latest_date} ｜ 生成时间: {generate_time} ｜ 数据来源: 银河证券</p>

<!-- ── 汇总卡片 ── -->
<div class="cards">
<div class="card">
<div class="card-label">持仓市值</div>
<div class="card-val">{mv}</div>
<div class="card-sub">共 {hc} 只持仓</div>
</div>
<div class="card">
<div class="card-label">当日盈亏 / 收益率</div>
<div class="card-val {dp_cls}">{dp}</div>
<div class="card-sub {dp_cls}">{dp_rate}%</div>
</div>
<div class="card">
<div class="card-label">累计总盈亏</div>
<div class="card-val placeholder">—</div>
<div class="card-sub">建仓以来</div>
</div>
<div class="card">
<div class="card-label">账户总价值(含现金)</div>
<div class="card-val placeholder">—</div>
<div class="card-sub">待后续补充</div>
</div>
<div class="card">
<div class="card-label">累计时间加权收益率</div>
<div class="card-val placeholder">—</div>
<div class="card-sub">待后续补充</div>
</div>
</div>

<!-- ── 当前持仓表格 ── -->
<div class="section">
<div class="section-title">📋 当前持仓</div>
<div class="chart-box" style="overflow-x:auto">
<table id="holdings-table">
<thead><tr>
<th>代码</th><th>名称</th><th>仓位占比</th><th>最新价</th>
<th>持有数量</th><th>持有金额</th><th>持有盈亏</th>
<th>持有盈亏率</th><th>持仓天数</th>
</tr></thead>
<tbody id="holdings-body"></tbody>
</table>
</div>
</div>

<!-- ── 累计收益曲线 ── -->
<div class="section">
<div class="section-title">📈 累计已实现收益</div>
<div class="chart-box"><div class="chart" id="chart-pnl"></div></div>
</div>

<!-- ── 收益率对比 ── -->
<div class="section">
<div class="section-title">📊 账户 vs 指数（归一化基值100）</div>
<div class="chart-box"><div class="chart" id="chart-compare"></div></div>
</div>

<!-- ── 已清仓分析 ── -->
<div class="section">
<div class="section-title">📦 已清仓盈亏</div>
<div class="closed-grid">
<div class="chart-box"><div class="chart-sm" id="chart-closed-a"></div></div>
<div class="chart-box"><div class="chart-sm" id="chart-closed-hk"></div></div>
</div>
</div>

<!-- ── 虚拟现金账户 ── -->
<div class="section">
<div class="section-title">💰 现金账户</div>
<div class="cards">
<div class="card"><div class="card-label">累计净入金</div><div class="card-val">{nd}</div></div>
</div>
</div>

<!-- ── 历史年度盈亏 ── -->
<div class="section">
<div class="section-title">📅 历史年度盈亏</div>
<div class="chart-box"><div class="chart" id="chart-yearly"></div></div>
</div>

<div class="footer">辰影的自由之路 ｜ 数据基于银河证券导出 ｜ 自动生成于 {generate_time}</div>

<script>
const D = {data_json};

const COLORS = {{
    up: '#3fb950', down: '#f85149', neutral: '#6e7681',
    bg: '#0d1117', cardBg: '#161b22', border: '#30363d',
    blue: '#58a6ff', cyan: '#39d353', orange: '#d2991d', purple: '#bc8cff'
}};
const chartTheme = {{
    backgroundColor: 'transparent',
    textStyle: {{ color: '#6e7681', fontSize: 11 }},
    grid: {{ top: 40, right: 20, bottom: 30, left: 60 }}
}};

// ── 1. 持仓表格 ──
(function() {{
    const h = D.holdings;
    const tb = document.getElementById('holdings-body');
    tb.innerHTML = h.map(r => {{
        const cls = v => v >= 0 ? 'positive' : 'negative';
        return `<tr>
            <td>${{r.code}}</td>
            <td>${{r.name}}</td>
            <td>${{r.weight.toFixed(1)}}%</td>
            <td>${{r.price.toFixed(2)}}</td>
            <td>${{r.qty.toLocaleString()}}</td>
            <td>${{r.market_value.toLocaleString(undefined,{{minimumFractionDigits:0,maximumFractionDigits:0}})}}</td>
            <td class="${{cls(r.hold_pnl)}}">${{r.hold_pnl.toLocaleString(undefined,{{minimumFractionDigits:0,maximumFractionDigits:0}})}}</td>
            <td class="${{cls(r.hold_pnl_rate)}}">${{r.hold_pnl_rate.toFixed(2)}}%</td>
            <td>${{r.days}}</td>
        </tr>`;
    }}).join('');
}})();

// ── 2. 累计收益曲线 ──
(function() {{
    const c = echarts.init(document.getElementById('chart-pnl'));
    const seq = D.cum_pnl_seq;
    const dates = seq.map(d => d.date);
    const pnls = seq.map(d => d.cum_pnl);
    c.setOption({{
        ...chartTheme,
        tooltip: {{ trigger:'axis', formatter: p => p[0].axisValue + '<br/>累计已实现: <b>' + (p[0].value/10000).toFixed(2) + '万</b>' }},
        xAxis: {{ type:'category', data:dates, axisLabel:{{rotate:30,formatter:v=>v.slice(5)}} }},
        yAxis: {{ type:'value', axisLabel:{{formatter:v=>(v/10000).toFixed(0)+'万'}}, splitLine:{{lineStyle:{{color:'#21262d'}}}} }},
        series: [{{
            type:'line', data:pnls, smooth:true, symbol:'none',
            lineStyle:{{color:COLORS.blue,width:2}},
            areaStyle:{{color:new echarts.graphic.LinearGradient(0,0,0,1,[{{offset:0,color:'rgba(88,166,255,0.3)'}},{{offset:1,color:'rgba(88,166,255,0.02)'}}])}},
            markLine:{{data:[{{yAxis:0,label:{{formatter:'零轴'}},lineStyle:{{color:'#484f58',type:'dashed'}}}}]}}
        }}]
    }});
    window.addEventListener('resize',()=>c.resize());
}})();

// ── 3. 收益率对比 ──
(function() {{
    const c = echarts.init(document.getElementById('chart-compare'));
    const idx = D.index_normalized;
    const dates = Object.keys(idx['沪深300']||{{}}).sort();
    if (dates.length === 0) {{ document.getElementById('chart-compare').parentElement.innerHTML='<p style=text-align:center;color:#6e7681;padding:40px>指数数据加载中...</p>'; return; }}
    const series = [
        {{ name:'沪深300', data:[], lineStyle:{{color:'#bc8cff',width:1.5}}, symbol:'none' }},
        {{ name:'创业板指', data:[], lineStyle:{{color:'#58a6ff',width:1.5}}, symbol:'none' }},
        {{ name:'上证指数', data:[], lineStyle:{{color:'#6e7681',width:1.5}}, symbol:'none' }},
    ];
    dates.forEach(d => {{
        series[0].data.push(idx['沪深300'][d] || null);
        series[1].data.push(idx['创业板指'][d] || null);
        series[2].data.push(idx['上证指数'][d] || null);
    }});
    c.setOption({{
        ...chartTheme,
        tooltip: {{ trigger:'axis' }},
        legend: {{ data:['沪深300','创业板指','上证指数'], textStyle:{{color:'#6e7681',fontSize:10}}, top:5 }},
        xAxis: {{ type:'category', data:dates, axisLabel:{{rotate:30,formatter:v=>v.slice(5)}} }},
        yAxis: {{ type:'value', axisLabel:{{formatter:v=>v.toFixed(0)}}, splitLine:{{lineStyle:{{color:'#21262d'}}}} }},
        series: series.map(s => ({{...s, type:'line'}}))
    }});
    window.addEventListener('resize',()=>c.resize());
}})();

// ── 4. 已清仓柱状图 ──
function buildClosedChart(domId, items, title) {{
    if (!items || items.length === 0) {{ document.getElementById(domId).parentElement.innerHTML='<p style=text-align:center;color:#6e7681;padding:40px>暂无数据</p>'; return; }}
    items.sort((a,b) => b.pnl - a.pnl);
    const c = echarts.init(document.getElementById(domId));
    c.setOption({{
        ...chartTheme,
        grid: {{ top:35, right:10, bottom:20, left:85 }},
        title: {{ text:title, textStyle:{{color:'#c9d1d9',fontSize:13}}, left:'center', top:5 }},
        tooltip: {{ trigger:'axis', formatter: p => p[0].name + '<br/>盈亏: <b>' + (p[0].value/10000).toFixed(2) + '万</b>' }},
        xAxis: {{ type:'value', axisLabel:{{formatter:v=>(v/10000).toFixed(1)+'万'}}, splitLine:{{lineStyle:{{color:'#21262d'}}}} }},
        yAxis: {{ type:'category', data:items.map(i=>i.name), inverse:true, axisLabel:{{fontSize:10,width:80,overflow:'truncate'}} }},
        series:[{{
            type:'bar', data:items.map(i=>({{value:i.pnl,itemStyle:{{color:i.pnl>=0?COLORS.up:COLORS.down}}}})),
            barWidth:14, label:{{show:true,position:'right',fontSize:9,formatter:p=>(p.value/10000).toFixed(1)+'万',color:'#6e7681'}}
        }}]
    }});
    window.addEventListener('resize',()=>c.resize());
}}
buildClosedChart('chart-closed-a', D.closed_analysis['A股']||[], 'A股已清仓');
buildClosedChart('chart-closed-hk', D.closed_analysis['港股']||[], '港股已清仓');

// ── 5. 年度盈亏 ──
(function() {{
    const yd = D.yearly_data;
    if (!yd || yd.length === 0) {{ document.getElementById('chart-yearly').parentElement.innerHTML='<p style=text-align:center;color:#6e7681;padding:40px>暂无数据</p>'; return; }}
    const c = echarts.init(document.getElementById('chart-yearly'));
    const years = yd.map(d => d.year);
    const pnls = yd.map(d => d.pnl);
    let cum = 0;
    const cumPnl = pnls.map(p => {{ cum += p; return cum; }});
    c.setOption({{
        ...chartTheme,
        tooltip: {{ trigger:'axis' }},
        legend: {{ data:['当年盈亏','累计盈亏'], textStyle:{{color:'#6e7681',fontSize:10}}, top:5 }},
        xAxis: {{ type:'category', data:years }},
        yAxis: [
            {{ type:'value', name:'当年(万)', nameTextStyle:{{color:'#6e7681',fontSize:10}}, axisLabel:{{formatter:v=>(v/10000).toFixed(0)+'万'}}, splitLine:{{lineStyle:{{color:'#21262d'}}}} }},
            {{ type:'value', name:'累计(万)', nameTextStyle:{{color:'#6e7681',fontSize:10}}, axisLabel:{{formatter:v=>(v/10000).toFixed(0)+'万'}} }}
        ],
        series:[
            {{ name:'当年盈亏', type:'bar', data:pnls.map(v=>({{value:v,itemStyle:{{color:v>=0?COLORS.up:COLORS.down}}}})), barWidth:32, label:{{show:true,position:'top',fontSize:10,formatter:p=>(p.value/10000).toFixed(1)+'万',color:'#6e7681'}} }},
            {{ name:'累计盈亏', type:'line', yAxisIndex:1, data:cumPnl, smooth:true, symbol:'circle', symbolSize:6, lineStyle:{{color:COLORS.orange,width:2.5}} }}
        ]
    }});
    window.addEventListener('resize',()=>c.resize());
}})();
</script>
</body>
</html>'''

# ── 格式化 ──
d = DATA; s = d["summary"]

def fmt_w(v):
    if v is None: return "—"
    if abs(v) >= 10000: return f"{v/10000:.1f}万"
    return f"{v:,.0f}"

def cls(v):
    if v is None: return ""
    return "up" if v >= 0 else "down"

mv = fmt_w(s["market_value"])
dp = fmt_w(s["day_pnl"])
dp_rate = f"{s['day_pnl_rate']:+.2f}" if s["day_pnl_rate"] is not None else "—"
nd = fmt_w(s["net_deposit"])

html = HTML.format(
    title=d["title"],
    latest_date=d["latest_date"],
    generate_time=d["generate_time"],
    mv=mv, hc=len(d["holdings"]),
    dp=dp, dp_rate=dp_rate, dp_cls=cls(s["day_pnl"]),
    nd=nd,
    data_json=json.dumps(d, ensure_ascii=False)
)

out_name = f"银河{d['latest_date']}_{ts}.HTML"
out_path = os.path.join(BASE_DIR, "output", out_name)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ HTML 已生成: {out_path}")
print(f"   大小: {len(html):,} 字符")
