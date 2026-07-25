#!/usr/bin/env python3
"""generate_html.py — 从 data.json 生成内嵌数据的自包含 HTML 看板"""

import json, os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "output", "data.json")) as f:
    DATA = json.load(f)

ts = datetime.now().strftime("%H%M%S")

HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0d1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;padding:20px;max-width:1200px;margin:0 auto}}
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
table{{width:100%;border-collapse:collapse;font-size:12px;background:#161b22;border-radius:8px;overflow:hidden}}
th{{background:#21262d;color:#c9d1d9;padding:8px 6px;text-align:center;font-weight:500;border-bottom:1px solid #30363d;white-space:nowrap}}
th:first-child,th:nth-child(2){{text-align:left}}
td{{padding:7px 6px;text-align:center;border-bottom:1px solid #21262d;white-space:nowrap}}
td:first-child,td:nth-child(2){{text-align:left}}
tr:hover{{background:#1c2129}}
.positive{{color:#3fb950}}
.negative{{color:#f85149}}
.footer{{text-align:center;font-size:10px;color:#484f58;margin-top:30px;padding:15px 0;border-top:1px solid #21262d}}
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
<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;overflow-x:auto">
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

<div class="footer">辰影的自由之路 ｜ 数据基于银河证券导出 ｜ 自动生成于 {generate_time}</div>

<script>
const D = {data_json};

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

html = HTML.format(
    title=d["title"],
    latest_date=d["latest_date"],
    generate_time=d["generate_time"],
    mv=fmt_w(s["market_value"]), hc=len(d["holdings"]),
    dp=fmt_w(s["day_pnl"]), dp_rate=f"{s['day_pnl_rate']:+.2f}" if s["day_pnl_rate"] is not None else "—",
    dp_cls=cls(s["day_pnl"]),
    data_json=json.dumps(d, ensure_ascii=False)
)

out_name = f"银河{d['latest_date']}_{ts}.HTML"
out_path = os.path.join(BASE_DIR, "output", out_name)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ {out_name}")
print(f"   {len(html):,} 字符")
