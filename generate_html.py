#!/usr/bin/env python3
"""generate_html.py — 从 data.json 生成内嵌数据的自包含 HTML 看板"""

import json, os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "output", "data.json")) as f:
    DATA = json.load(f)

ts = (datetime.now() + __import__('datetime').timedelta(hours=8)).strftime("%H%M%S")  # 北京时间

HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0d1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;padding:12px;max-width:1200px;margin:0 auto}}
h1{{text-align:center;font-size:18px;color:#f0f6fc;margin:8px 0 3px;letter-spacing:1px}}
.subtitle{{text-align:center;font-size:11px;color:#6e7681;margin-bottom:14px}}
.cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:16px}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:10px 8px;text-align:center}}
.card-label{{font-size:10px;color:#6e7681;margin-bottom:2px}}
.card-val{{font-size:18px;font-weight:700;color:#f0f6fc;line-height:1.2}}
.card-val.up{{color:#f85149}}
.card-val.down{{color:#3fb950}}
.card-sub{{font-size:10px;color:#6e7681;margin-top:1px}}
.section{{margin-bottom:20px}}
.section-title{{font-size:14px;font-weight:600;color:#f0f6fc;margin-bottom:8px;padding-left:8px;border-left:3px solid #58a6ff}}
table{{width:100%;table-layout:fixed;border-collapse:collapse;font-size:12px;background:#161b22;border-radius:8px;overflow:hidden}}
.filter-bar{{display:flex;gap:4px;margin-bottom:6px;align-items:center}}
.filter-bar input{{background:#21262d;border:1px solid #30363d;color:#c9d1d9;padding:4px 4px;border-radius:4px;font-size:11px;min-width:0}}
.filter-bar select{{background:#21262d;border:1px solid #30363d;color:#c9d1d9;padding:4px 6px;border-radius:4px;font-size:11px}}
.filter-active{{border-color:#58a6ff!important;box-shadow:0 0 0 1px #58a6ff}}
.sort-arrow{{font-size:10px;margin-left:2px;opacity:0.5}}
.sort-arrow.active{{opacity:1;color:#58a6ff}}
th{{background:#21262d;color:#c9d1d9;padding:8px 4px;text-align:center;font-weight:500;border-bottom:1px solid #30363d;white-space:nowrap;cursor:pointer;user-select:none;position:sticky;top:0;z-index:1}}
th:hover{{background:#2d3741}}
th:first-child,th:nth-child(2){{text-align:left}}
td{{padding:6px 4px;text-align:center;border-bottom:1px solid #21262d;white-space:nowrap;font-size:12px}}
td:first-child,td:nth-child(2){{text-align:left}}
tr:hover{{background:#1c2129}}
.positive{{color:#f85149}}
.negative{{color:#3fb950}}
.footer{{text-align:center;font-size:10px;color:#484f58;margin-top:24px;padding:12px 0;border-top:1px solid #21262d}}
.placeholder{{color:#484f58;font-size:18px}}
.no-result{{text-align:center;padding:20px;color:#6e7681;font-size:13px}}
@media(max-width:768px){{
  .cards{{grid-template-columns:repeat(3,1fr)}}
  .card-val{{font-size:15px}}
  .card{{padding:8px 6px}}
  th,td{{font-size:11px;padding:5px 4px}}
}}
@media(max-width:480px){{
  .cards{{grid-template-columns:repeat(2,1fr);gap:5px}}
  .card-val{{font-size:14px}}
  .card-label{{font-size:9px}}
  h1{{font-size:16px}}
  body{{padding:8px}}
}}
</style>
</head>
<body>

<h1>{title}</h1>
<p class="subtitle">数据日期: {latest_date} ｜ 生成时间: {generate_time} ｜ 数据来源: 银河证券</p>

<!-- ── 汇总卡片 ── -->
<div class="section">
<div class="section-title">📋 汇总</div>
<div class="cards">
<div class="card">
<div class="card-label">股票持仓市值 / 占比</div>
<div class="card-val">{mv}<span style="font-size:13px;color:#6e7681">/{mv_pct}%</span></div>
<div class="card-sub">共 {hc} 只持仓</div>
</div>
<div class="card">
<div class="card-label">现金 / 占比</div>
<div class="card-val">{cash}<span style="font-size:13px;color:#6e7681">/{cash_pct}%</span></div>
<div class="card-sub">国债逆回购</div>
</div>
<div class="card">
<div class="card-label">总市值</div>
<div class="card-val">{tv}</div>
<div class="card-sub">股票+现金</div>
</div>
<div class="card">
<div class="card-label">当日盈亏 / 收益率</div>
<div class="card-val {dp_cls}">{dp}<span style="font-size:13px;color:#6e7681">/{dp_rate}%</span></div>
<div class="card-sub">{date_cn}</div>
</div>
<div class="card">
<div class="card-label">持仓总盈亏 / 已清仓总盈亏</div>
<div class="card-val {cp_cls}">{cp}<span style="font-size:13px;color:#6e7681">/{closed_pnl}</span></div>
<div class="card-sub">建仓以来</div>
</div>
</div>
</div>

<!-- ── 当前持仓表格 ── -->
<div class="section">
<div class="section-title">📋 当前持仓 <span style="font-size:11px;color:#6e7681;font-weight:400;margin-left:8px">点击表头排序 | 输入关键词筛选</span></div>
<div class="filter-bar">
  <button onclick="resetDefault()" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:10px;white-space:nowrap">↻ 默认</button>
  <input type="text" id="f-code" placeholder="代码" style="width:70px">
  <input type="text" id="f-name" placeholder="名称" style="width:90px">
  <input type="text" id="f-weight" placeholder="仓位≥%" style="width:60px">
  <input type="text" id="f-price" placeholder="现价≥" style="width:60px">
  <input type="text" id="f-qty" placeholder="数量≥" style="width:60px">
  <input type="text" id="f-mv" placeholder="市值≥" style="width:65px">
  <input type="text" id="f-pnl" placeholder="盈亏≥" style="width:60px">
  <input type="text" id="f-pnlrate" placeholder="盈亏率≥" style="width:65px">
  <input type="text" id="f-days" placeholder="天数≥" style="width:50px">
  <button onclick="clearFilters()" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:10px;white-space:nowrap">✕</button>
</div>
<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;overflow-x:auto">
<table id="holdings-table">
<thead><tr>
<th data-col="code">代码</th>
<th data-col="name">名称</th>
<th data-col="weight">仓位占比</th>
<th data-col="price">最新价</th>
<th data-col="qty">持有数量</th>
<th data-col="market_value">持有金额</th>
<th data-col="hold_pnl">持有盈亏</th>
<th data-col="hold_pnl_rate">持有盈亏率</th>
<th data-col="days">持仓天数</th>
</tr></thead>
<tbody id="holdings-body"></tbody>
</table>
</div>
</div>

<div class="footer">辰影的自由之路 ｜ 数据基于银河证券导出 ｜ 自动生成于 {generate_time}</div>

<script>
const D = {data_json};

let holdings, sortCol, sortDir;

// ── 排序（不切换方向，参数控制）──
function doSort(col, dir) {{
  sortCol = col; sortDir = dir || -1;
  holdings.sort((a,b) => {{
    let va = a[col]||0, vb = b[col]||0;
    if (typeof va === 'string') return sortDir * va.localeCompare(vb);
    return sortDir * (va - vb);
  }});
  renderTable();
  updateArrows();
}}

// ── 点击表头切换排序 ──
function toggleSort(col) {{
  if (sortCol === col) sortDir *= -1; else {{ sortCol = col; sortDir = -1; }}
  doSort(col, sortDir);
}}

// ── 筛选 ──
function applyFilters() {{
  const el = id => document.getElementById(id);
  const get = id => {{ const e=el(id); return e ? e.value.trim() : ''; }};
  const f_code = get('f-code').toLowerCase();
  const f_name = get('f-name').toLowerCase();
  const f_weight = parseFloat(get('f-weight'))||-1;
  const f_price = parseFloat(get('f-price'))||-1;
  const f_qty = parseFloat(get('f-qty'))||-1;
  const f_mv = parseFloat(get('f-mv'))||-1;
  const f_pnl = get('f-pnl'); const f_pnl_v = parseFloat(f_pnl)||-999999;
  const f_rate = get('f-pnlrate'); const f_rate_v = parseFloat(f_rate)||-999;
  const f_days = parseFloat(get('f-days'))||-1;
  return D.holdings.filter(r => {{
    if (f_code && !r.code.toLowerCase().includes(f_code)) return false;
    if (f_name && !r.name.toLowerCase().includes(f_name)) return false;
    if (f_weight>=0 && r.weight<f_weight) return false;
    if (f_price>0 && r.price<f_price) return false;
    if (f_qty>0 && r.qty<f_qty) return false;
    if (f_mv>0 && r.market_value<f_mv) return false;
    if (f_pnl && r.hold_pnl<f_pnl_v) return false;
    if (f_rate && r.hold_pnl_rate<f_rate_v) return false;
    if (f_days>0 && r.days<f_days) return false;
    return true;
  }});
}}

function clearFilters() {{
  document.querySelectorAll('.filter-bar input').forEach(el => {{ el.value = ''; el.classList.remove('filter-active'); }});
  holdings = applyFilters();
  if (sortCol) doSort(sortCol, sortDir);
  else renderTable();
}}

function resetDefault() {{
  document.querySelectorAll('.filter-bar input').forEach(el => {{ el.value = ''; el.classList.remove('filter-active'); }});
  holdings = D.holdings;
  doSort('weight', -1);
}}

// ── 渲染 ──
function renderTable() {{
  const tb = document.getElementById('holdings-body');
  if (!holdings || holdings.length===0) {{ tb.innerHTML='<tr><td colspan="9" class="no-result">无匹配结果</td></tr>'; return; }}
  tb.innerHTML = holdings.map(r => {{
    const c = v => v>=0?'positive':'negative';
    return '<tr><td>'+r.code+'</td><td>'+r.name+'</td><td>'+r.weight.toFixed(1)+'%</td><td>'+r.price.toFixed(2)+'</td><td>'+r.qty.toLocaleString()+'</td><td>'+r.market_value.toLocaleString(undefined,{{minimumFractionDigits:0,maximumFractionDigits:0}})+'</td><td class="'+c(r.hold_pnl)+'">'+r.hold_pnl.toLocaleString(undefined,{{minimumFractionDigits:0,maximumFractionDigits:0}})+'</td><td class="'+c(r.hold_pnl_rate)+'">'+r.hold_pnl_rate.toFixed(2)+'%</td><td>'+r.days+'</td></tr>';
  }}).join('');
}}

function updateArrows() {{
  document.querySelectorAll('th[data-col]').forEach(th => {{
    const a = th.querySelector('.sort-arrow');
    if (!a) return;
    const col = th.dataset.col;
    a.classList.toggle('active', col===sortCol);
    a.textContent = col===sortCol ? (sortDir===1?' ▲':' ▼') : ' ⇅';
  }});
}}

// ── 初始化 ──
(function init() {{
  // 箭头 + 点击
  document.querySelectorAll('th[data-col]').forEach(th => {{
    th.innerHTML += '<span class="sort-arrow"> ⇅</span>';
    th.addEventListener('click', () => toggleSort(th.dataset.col));
  }});
  // 筛选输入
  document.querySelectorAll('.filter-bar input').forEach(inp => {{
    const handler = () => {{
      try {{
        inp.classList.toggle('filter-active', inp.value.trim()!=='');
        holdings = applyFilters();
        if (sortCol) doSort(sortCol, sortDir); else renderTable();
      }} catch(e) {{ alert('筛选出错: '+e.message); }}
    }};
    inp.addEventListener('input', handler);
    inp.addEventListener('keyup', handler);
  }});
  // 默认渲染
  holdings = D.holdings;
  doSort('weight', -1);
}})();
</script>
</body>
</html>'''

d = DATA; s = d["summary"]

def fmt_w(v):
    if v is None: return "—"
    if abs(v) >= 10000: return f"{v/10000:.1f}万"
    return f"{v:,.0f}"

def cls(v):
    if v is None: return ""
    return "up" if v >= 0 else "down"

# 日期格式化
ld = d["latest_date"]
date_cn = f"{ld[:4]}年{int(ld[5:7])}月{int(ld[8:10])}日"

html = HTML.format(
    title=d["title"],
    latest_date=d["latest_date"],
    generate_time=d["generate_time"],
    date_cn=date_cn,
    mv=fmt_w(s["market_value"]), hc=len(d["holdings"]),
    mv_pct=round(s["market_value"]/s["total_value"]*100, 1) if s.get("total_value") else "—",
    dp=fmt_w(s["day_pnl"]), dp_rate=f"{s['day_pnl_rate']:+.2f}" if s["day_pnl_rate"] is not None else "—",
    dp_cls=cls(s["day_pnl"]),
    cash=fmt_w(s.get("cash")),
    cash_pct=round(s["cash"]/s["total_value"]*100, 1) if s.get("cash") and s.get("total_value") else "—",
    tv=fmt_w(s.get("total_value")),
    cp=fmt_w(s.get("cum_pnl")),
    cp_cls=cls(s.get("cum_pnl")),
    closed_pnl=fmt_w(s.get("closed_total_pnl")),
    data_json=json.dumps(d, ensure_ascii=False)
)

out_name = f"银河{d['latest_date']}_{ts}.HTML"
out_path = os.path.join(BASE_DIR, "output", out_name)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ {out_name}")
print(f"   {len(html):,} 字符")
