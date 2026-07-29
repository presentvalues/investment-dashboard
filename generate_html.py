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
<script src="https://registry.npmmirror.com/echarts/5.5.0/files/dist/echarts.min.js" defer></script>
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

<!-- ── 账户收益率 ── -->
<div class="section">
<div class="section-title">📈 账户收益率 <span style="font-size:11px;color:#6e7681;font-weight:400;margin-left:8px">基准 {baseline_date} = 0%</span></div>
<div id="return-chart" style="width:100%;height:360px;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:8px;display:flex;align-items:center;justify-content:center;color:#6e7681;font-size:13px">📊 图表加载中…</div>
</div>

<!-- ── 已清仓股票累计收益/亏损 ── -->
<div class="section">
<div class="section-title">📋 已清仓股票累计收益/亏损</div>
<p class="subtitle" style="font-size:11px;color:#6e7681;margin-bottom:10px;text-align:left">
已清仓 {closed_count} 只；累计已实现净额：<span style="color:{total_cls}">{total_pnl} 万元</span>，
其中 A 股净额：<span style="color:{a_cls}">{a_pnl} 万元</span>，
港股净额：<span style="color:{h_cls}">{h_pnl} 万元</span>
</p>
<div style="display:flex;gap:12px">
  <div style="flex:1;min-width:0">
    <div style="font-size:12px;color:#c9d1d9;margin-bottom:6px;text-align:center">A 股盈亏前 5</div>
    <div id="closed-a-chart" style="width:100%;height:{chart_height}px;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:8px;display:flex;align-items:center;justify-content:center;color:#6e7681;font-size:13px">📊 图表加载中…</div>
  </div>
  <div style="flex:1;min-width:0">
    <div style="font-size:12px;color:#c9d1d9;margin-bottom:6px;text-align:center">港股盈亏前 5</div>
    <div id="closed-h-chart" style="width:100%;height:{chart_height}px;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:8px;display:flex;align-items:center;justify-content:center;color:#6e7681;font-size:13px">📊 图表加载中…</div>
  </div>
</div>
</div>

<!-- ── 历史年度盈亏 ── -->
<div class="section">
<div class="section-title">📈 历史年度盈亏（2021 年至今）</div>
<div id="yearly-chart" style="width:100%;height:320px;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:8px;display:flex;align-items:center;justify-content:center;color:#6e7681;font-size:13px">📊 图表加载中…</div>
<div id="yearly-table" style="margin-top:10px;overflow-x:auto"></div>
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

// ── 收益图（双Y轴：左=总市值柱状图，右=收益率折线）──
function renderReturnChart() {{
  if (!D.return_series || D.return_series.length < 2) return;
  const rs = D.return_series;
  const dates = rs.map(r => r.date.slice(5));
  const chart = echarts.init(document.getElementById('return-chart'));
  // 动态计算整数刻度：上限 = ceil(max/5)*5，每档 = 上限/5，零点下方对称一档
  const tvVals = rs.map(r => r.total_value).filter(v => v != null);
  const retVals = [].concat(rs.map(r => r.account), rs.map(r => r.shanghai), rs.map(r => r.csi300), rs.map(r => r.chinext)).filter(v => v != null);
  const tvMaxW = Math.max(...tvVals) / 10000;                     // 万为单位
  const retMin = Math.min(...retVals), retMax = Math.max(...retVals);
  // 左轴：50万为步长取整，保证柱子不超过上限的2/3
  const leftTopRaw = Math.ceil(tvMaxW / 50) * 50;
  const leftTop = (tvMaxW / leftTopRaw > 2/3) ? leftTopRaw + 50 : leftTopRaw;
  const leftStep = leftTop / 5;                                    // 每档（万）
  const rightTop = Math.ceil(retMax / 5) * 5;                     // 上限（%），5%步长
  const rightBottom = Math.floor(retMin / 5) * 5;                 // 下限（%），5%步长
  chart.setOption({{
    tooltip: {{
      trigger: 'axis',
      formatter: function(params) {{
        let s = '<b>' + params[0].axisValue + '</b><br/>';
        params.forEach(p => {{
          if (p.seriesName === '总市值') {{
            s += p.marker + ' ' + p.seriesName + ': ' + (p.value/10000).toFixed(2) + '万<br/>';
          }} else {{
            const v = p.value !== null ? p.value.toFixed(2) + '%' : '—';
            s += p.marker + ' ' + p.seriesName + ': ' + v + '<br/>';
          }}
        }});
        return s;
      }}
    }},
    legend: {{ data: ['总市值','账户','上证指数','沪深300','创业板'], top: 0, textStyle: {{ color: '#c9d1d9' }} }},
    grid: {{ left: '10%', right: '10%', top: '15%', bottom: '8%' }},
    xAxis: {{ type: 'category', data: dates, axisLabel: {{ color: '#6e7681', fontSize: 10 }} }},
    yAxis: [
      {{
        type: 'value', min: -(leftStep * 10000), max: leftTop * 10000, interval: leftStep * 10000,
        name: '总市值(万)',
        nameTextStyle: {{ color: '#6e7681', fontSize: 10 }},
        axisLabel: {{ formatter: v => (v/10000).toFixed(0), color: '#6e7681', fontSize: 10 }},
        splitLine: {{ lineStyle: {{ color: '#21262d' }} }}
      }},
      {{
        type: 'value', min: rightBottom, max: rightTop, interval: 5,
        name: '收益率(%)',
        nameTextStyle: {{ color: '#6e7681', fontSize: 10 }},
        axisLabel: {{ formatter: v => v.toFixed(0)+'%', color: '#6e7681', fontSize: 10 }},
        splitLine: {{ show: false }}
      }}
    ],
    series: [
      {{
        name: '总市值', type: 'bar', yAxisIndex: 0,
        data: rs.map(r => r.total_value),
        itemStyle: {{ color: 'rgba(88,166,255,0.35)', borderColor: '#58a6ff', borderWidth: 1 }},
        barWidth: '40%'
      }},
      {{
        name: '账户', type: 'line', yAxisIndex: 1,
        data: rs.map(r => r.account),
        lineStyle: {{ color: '#f85149', width: 2 }},
        itemStyle: {{ color: '#f85149' }},
        symbol: 'circle', symbolSize: 8, connectNulls: false,
        markLine: {{
          silent: true, symbol: 'none',
          lineStyle: {{ color: '#6e7681', type: 'dashed', width: 1 }},
          label: {{ show: false }},
          data: [{{ yAxis: 0 }}]
        }}
      }},
      {{
        name: '上证指数', type: 'line', yAxisIndex: 1,
        data: rs.map(r => r.shanghai),
        lineStyle: {{ color: '#ff8c00', width: 0.75 }},
        itemStyle: {{ color: '#ff8c00' }},
        symbol: 'diamond', symbolSize: 6
      }},
      {{
        name: '沪深300', type: 'line', yAxisIndex: 1,
        data: rs.map(r => r.csi300),
        lineStyle: {{ color: '#d2991d', width: 0.75 }},
        itemStyle: {{ color: '#d2991d' }},
        symbol: 'diamond', symbolSize: 6
      }},
      {{
        name: '创业板', type: 'line', yAxisIndex: 1,
        data: rs.map(r => r.chinext),
        lineStyle: {{ color: '#bb6bd9', width: 0.75 }},
        itemStyle: {{ color: '#bb6bd9' }},
        symbol: 'triangle', symbolSize: 7
      }}
    ]
  }});
  window.addEventListener('resize', () => chart.resize());
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
  // 年度数据表不等图表，直接渲染
  if (D.yearly_data) renderYearlyTable();
  // 图表：在线用 ECharts，离线超时 3 秒后切换纯 HTML 数据表
  var chartRendered = false;
  function tryRenderChart() {{
    if (chartRendered) return;
    if (typeof echarts !== 'undefined') {{
      chartRendered = true;
      renderReturnChart();
      // 已清仓图表
      if (D.closed_merged) {{
        renderClosedChart('closed-a-chart', D.closed_merged.a_stock, 'A股');
        renderClosedChart('closed-h-chart', D.closed_merged.h_stock, '港股');
      }}
      // 年度盈亏图表
      if (D.yearly_data) renderYearlyChart();
    }}
  }}
  tryRenderChart();
  if (!chartRendered) {{
    document.addEventListener('DOMContentLoaded', function() {{
      tryRenderChart();
      if (!chartRendered) {{
        setTimeout(function() {{
          if (!chartRendered) {{
            renderReturnFallback();
            if (D.closed_merged) {{
              renderClosedFallback('closed-a-chart', D.closed_merged.a_stock);
              renderClosedFallback('closed-h-chart', D.closed_merged.h_stock);
            }}
            if (D.yearly_data) renderYearlyFallback();
          }}
        }}, 3000);
      }}
    }});
  }}
}})();

// ── 离线降级：纯 HTML 收益率数据表 ──
function renderReturnFallback() {{
  var rs = D.return_series;
  if (!rs || rs.length === 0) return;
  var el = document.getElementById('return-chart');
  var html = '<table style="width:100%;border-collapse:collapse;font-size:12px;color:#c9d1d9">';
  html += '<thead><tr style="background:#21262d">';
  html += '<th style="padding:6px 8px;text-align:left;border-bottom:1px solid #30363d">日期</th>';
  html += '<th style="padding:6px 8px;text-align:right;border-bottom:1px solid #30363d">账户</th>';
  html += '<th style="padding:6px 8px;text-align:right;border-bottom:1px solid #30363d">上证指数</th>';
  html += '<th style="padding:6px 8px;text-align:right;border-bottom:1px solid #30363d">沪深300</th>';
  html += '<th style="padding:6px 8px;text-align:right;border-bottom:1px solid #30363d">创业板</th>';
  html += '</tr></thead><tbody>';
  var colors = ['#f85149','#ff8c00','#d2991d','#bb6bd9'];
  rs.forEach(function(r) {{
    html += '<tr>';
    html += '<td style="padding:5px 8px;border-bottom:1px solid #21262d">' + r.date.slice(5) + '</td>';
    [r.account, r.shanghai, r.csi300, r.chinext].forEach(function(v, i) {{
      var color = v !== null ? colors[i] : '#484f58';
      var text = v !== null ? (v >= 0 ? '+' : '') + v.toFixed(2) + '%' : '—';
      html += '<td style="padding:5px 8px;text-align:right;border-bottom:1px solid #21262d;color:' + color + '">' + text + '</td>';
    }});
    html += '</tr>';
  }});
  html += '</tbody></table>';
  html += '<div style="text-align:center;font-size:10px;color:#484f58;margin-top:8px">离线模式 · 联网可显示交互图表</div>';
  el.innerHTML = html;
  el.style.display = 'block';
  el.style.padding = '12px';
}}

// ── 已清仓横向柱状图 ──
function renderClosedChart(containerId, data, title) {{
  if (!data || (data.profit.length === 0 && data.loss.length === 0)) {{
    document.getElementById(containerId).innerHTML = '<span style="color:#6e7681">暂无数据</span>';
    return;
  }}
  // 合并盈亏数据：盈利在上（正值），亏损在下（负值）
  var categories = [];
  var values = [];
  var codes = [];
  data.profit.forEach(function(x) {{
    categories.push(x.code + ' ' + x.name);
    values.push(x.pnl / 10000);
    codes.push(x.code);
  }});
  data.loss.forEach(function(x) {{
    categories.push(x.code + ' ' + x.name);
    values.push(x.pnl / 10000);
    codes.push(x.code);
  }});

  // 动态坐标轴范围：以5万为步长向上取整
  var maxProfit = 0, maxLoss = 0;
  values.forEach(function(v) {{
    if (v > maxProfit) maxProfit = v;
    if (v < -maxLoss) maxLoss = -v;
  }});
  var axisMax = Math.ceil(Math.max(maxProfit, maxLoss, 0.01) / 5) * 5;
  axisMax = Math.max(axisMax, 5);

  var el = document.getElementById(containerId);
  var chart = echarts.init(el);
  chart.setOption({{
    tooltip: {{
      trigger: 'axis',
      axisPointer: {{ type: 'shadow' }},
      formatter: function(params) {{
        var p = params[0];
        var v = p.value;
        var sign = v >= 0 ? '+' : '';
        return p.name + '<br/>盈亏: ' + sign + v.toFixed(2) + '万';
      }}
    }},
    grid: {{ left: '2%', right: '8%', top: 5, bottom: 5, containLabel: true }},
    xAxis: {{
      type: 'value', min: -axisMax, max: axisMax, interval: axisMax / 5,
      axisLabel: {{ show: false }},
      axisTick: {{ show: false }},
      splitLine: {{ show: false }},
      axisLine: {{ show: false }}
    }},
    yAxis: {{
      type: 'category', data: categories, inverse: true,
      axisLabel: {{ color: '#c9d1d9', fontSize: 10, width: 85, overflow: 'truncate' }},
      axisLine: {{ lineStyle: {{ color: '#30363d' }} }}
    }},
    series: [{{
      type: 'bar',
      data: values.map(function(v, i) {{
        return {{
          value: v,
          itemStyle: {{ color: v >= 0 ? '#f85149' : '#3fb950' }},
          label: {{
            show: true,
            position: v >= 0 ? 'right' : 'left',
            formatter: function(p) {{ return (p.value >= 0 ? '+' : '') + p.value.toFixed(2) + '万'; }},
            color: '#c9d1d9', fontSize: 10
          }}
        }};
      }}),
      barWidth: 16
    }}]
  }});
  window.addEventListener('resize', function() {{ chart.resize(); }});
}}

// 已清仓图表降级
function renderClosedFallback(containerId, data) {{
  if (!data) return;
  var all = (data.profit||[]).concat(data.loss||[]);
  if (all.length===0) return;
  var el = document.getElementById(containerId);
  var html = '<table style="width:100%;font-size:11px;color:#c9d1d9;border-collapse:collapse">';
  all.forEach(function(x) {{
    var w = x.pnl / 10000;
    var color = w >= 0 ? '#f85149' : '#3fb950';
    var sign = w >= 0 ? '+' : '';
    html += '<tr><td style="padding:2px 4px;border-bottom:1px solid #21262d">' + x.code + '</td>';
    html += '<td style="padding:2px 4px;border-bottom:1px solid #21262d">' + x.name + '</td>';
    html += '<td style="padding:2px 4px;text-align:right;border-bottom:1px solid #21262d;color:' + color + '">' + sign + w.toFixed(2) + '万</td></tr>';
  }});
  html += '</table>';
  el.innerHTML = html;
  el.style.display = 'block';
  el.style.padding = '8px';
}}

// ── 历史年度盈亏图（竖向柱状：当年盈亏 + 累计盈亏折线，单轴）──
function renderYearlyChart() {{
  var yd = D.yearly_data;
  if (!yd || !yd.years || yd.years.length === 0) return;
  var years = yd.years.map(function(y) {{ return y.year.toString(); }});
  var pnlData = yd.years.map(function(y) {{ return (y.pnl / 10000); }});
  var cumData = yd.cum_pnl.map(function(c) {{ return c.value; }});

  var pnlAbs = Math.max(Math.abs(Math.min.apply(null, pnlData)), Math.abs(Math.max.apply(null, pnlData)), 0.1);
  var cumAbs = Math.max(Math.abs(Math.min.apply(null, cumData)), Math.abs(Math.max.apply(null, cumData)), 0.1);
  var axisMax = Math.ceil(Math.max(pnlAbs, cumAbs) / 10) * 10;
  axisMax = Math.max(axisMax, 10);
  var axisStep = axisMax / 5;

  var el = document.getElementById('yearly-chart');
  var chart = echarts.init(el);
  chart.setOption({{
    tooltip: {{
      trigger: 'axis',
      formatter: function(params) {{
        var s = '<b>' + params[0].axisValue + '</b><br/>';
        params.forEach(function(p) {{
          if (p.seriesName === '累计盈亏') {{
            s += p.marker + ' ' + p.seriesName + ': ' + (p.value >= 0 ? '+' : '') + p.value.toFixed(2) + '万<br/>';
          }} else {{
            s += p.marker + ' ' + p.seriesName + ': ' + (p.value >= 0 ? '+' : '') + p.value.toFixed(2) + '万';
          }}
        }});
        return s;
      }}
    }},
    legend: {{ data: ['当年盈亏','累计盈亏'], top: 0, textStyle: {{ color: '#c9d1d9' }} }},
    grid: {{ left: '10%', right: '6%', top: '15%', bottom: '10%' }},
    xAxis: {{ type: 'category', data: years, boundaryGap: false, axisLabel: {{ color: '#6e7681', fontSize: 10, margin: 8 }} }},
    yAxis: {{
      type: 'value', min: -(axisMax), max: axisMax, interval: axisStep,
      name: '万元', nameTextStyle: {{ color: '#6e7681', fontSize: 10 }},
      axisLabel: {{ formatter: function(v) {{ return v.toFixed(0); }}, color: '#6e7681', fontSize: 10 }},
      splitLine: {{ lineStyle: {{ color: '#21262d' }} }}
    }},
    series: [
      {{
        name: '当年盈亏', type: 'bar',
        data: pnlData.map(function(v) {{
          return {{ value: v, itemStyle: {{ color: v >= 0 ? '#f85149' : '#3fb950' }} }};
        }}),
        barWidth: '45%'
      }},
      {{
        name: '累计盈亏', type: 'line',
        data: cumData,
        lineStyle: {{ color: '#58a6ff', width: 3 }},
        itemStyle: {{ color: '#58a6ff' }},
        symbol: 'circle', symbolSize: 8
      }}
    ]
  }});
  window.addEventListener('resize', function() {{ chart.resize(); }});
}}

// 年度数据表（始终渲染，不等 ECharts）
function renderYearlyTable() {{
  var yd = D.yearly_data;
  if (!yd || !yd.years) return;
  var el = document.getElementById('yearly-table');
  var cols = [
    {{key:'year', title:'年份', fmt:function(v){{return v;}} }},
    {{key:'pnl', title:'当年盈亏(万)', fmt:function(v){{return (v>=0?'+':'')+v.toFixed(1);}}, cls:function(v){{return v>=0?'positive':'negative';}} }},
    {{key:'twr', title:'时间加权收益', fmt:function(v){{return v.toFixed(2)+'%';}}, cls:function(v){{return v>=0?'positive':'negative';}} }},
    {{key:'mwr', title:'资金加权收益', fmt:function(v){{return v.toFixed(2)+'%';}}, cls:function(v){{return v>=0?'positive':'negative';}} }},
    {{key:'dividend', title:'中证红利全收益', fmt:function(v){{return v.toFixed(2)+'%';}}, cls:function(v){{return v>=0?'positive':'negative';}} }},
    {{key:'csi300', title:'沪深300全收益', fmt:function(v){{return v.toFixed(2)+'%';}}, cls:function(v){{return v>=0?'positive':'negative';}} }},
    {{key:'chinext', title:'创业板全收益', fmt:function(v){{return v.toFixed(2)+'%';}}, cls:function(v){{return v>=0?'positive':'negative';}} }},
    {{key:'hsi', title:'恒生指数', fmt:function(v){{return v.toFixed(2)+'%';}}, cls:function(v){{return v>=0?'positive':'negative';}} }},
    {{key:'sp500', title:'标普500', fmt:function(v){{return v.toFixed(2)+'%';}}, cls:function(v){{return v>=0?'positive':'negative';}} }}
  ];
  var html = '<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;overflow-x:auto">';
  html += '<table style="width:100%;border-collapse:collapse;font-size:12px;color:#c9d1d9">';
  html += '<thead><tr style="background:#21262d">';
  cols.forEach(function(c) {{
    html += '<th style="padding:6px 6px;border-bottom:1px solid #30363d;white-space:nowrap;text-align:center">' + c.title + '</th>';
  }});
  html += '</tr></thead><tbody>';
  yd.years.forEach(function(y) {{
    html += '<tr>';
    cols.forEach(function(c) {{
      var v = c.key==='year' ? y.year : (c.key==='pnl' ? y.pnl/10000 : y[c.key]);
      var cls = c.cls ? c.cls(v) : '';
      html += '<td style="padding:5px 6px;border-bottom:1px solid #21262d;text-align:center" class="' + cls + '">' + c.fmt(v) + '</td>';
    }});
    html += '</tr>';
  }});
  html += '</tbody></table></div>';
  el.innerHTML = html;
}}

// 年度盈亏离线降级（图表区用简洁文字替代）
function renderYearlyFallback() {{
  var yd = D.yearly_data;
  if (!yd || !yd.years) return;
  var el = document.getElementById('yearly-chart');
  var html = '<table style="width:100%;border-collapse:collapse;font-size:12px;color:#c9d1d9">';
  html += '<thead><tr style="background:#21262d">';
  html += '<th style="padding:6px 8px;border-bottom:1px solid #30363d">年份</th>';
  html += '<th style="padding:6px 8px;text-align:right;border-bottom:1px solid #30363d">当年盈亏</th>';
  html += '<th style="padding:6px 8px;text-align:right;border-bottom:1px solid #30363d">TWR</th>';
  html += '<th style="padding:6px 8px;text-align:right;border-bottom:1px solid #30363d">MWR</th>';
  html += '</tr></thead><tbody>';
  yd.years.forEach(function(y, i) {{
    var pnl = y.pnl / 10000;
    var pc = pnl >= 0 ? '#f85149' : '#3fb950';
    html += '<tr>';
    html += '<td style="padding:5px 8px;border-bottom:1px solid #21262d">' + y.year + '</td>';
    html += '<td style="padding:5px 8px;text-align:right;border-bottom:1px solid #21262d;color:' + pc + '">' + (pnl >= 0 ? '+' : '') + pnl.toFixed(2) + '万</td>';
    html += '<td style="padding:5px 8px;text-align:right;border-bottom:1px solid #21262d;color:#58a6ff">' + yd.twr[i].value.toFixed(2) + '%</td>';
    html += '<td style="padding:5px 8px;text-align:right;border-bottom:1px solid #21262d;color:#d2991d">' + yd.mwr[i].value.toFixed(2) + '%</td>';
    html += '</tr>';
  }});
  html += '</tbody></table>';
  html += '<div style="text-align:center;font-size:10px;color:#484f58;margin-top:8px">离线模式 · 联网可显示交互图表</div>';
  el.innerHTML = html;
  el.style.display = 'block';
  el.style.padding = '12px';
}}
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
weekdays = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
dt = datetime.strptime(ld, "%Y-%m-%d")
date_cn = f"{ld[:4]}年{int(ld[5:7])}月{int(ld[8:10])}日（{weekdays[dt.weekday()]}）"

# 基准日期
bd = d.get("return_series") and d["return_series"][0]["date"] if d.get("return_series") else d["latest_date"]
baseline_date_cn = f"{bd[:4]}年{int(bd[5:7])}月{int(bd[8:10])}日" if bd else date_cn

# 已清仓板块数据
cm = d.get("closed_merged", {})
cms = cm.get("summary", {})
if cms:
    closed_count = cms.get("count", 0)
    total_pnl = f"{cms['total_pnl']/10000:+.2f}" if cms.get("total_pnl") else "0.00"
    a_pnl = f"{cms['a_total']/10000:+.2f}" if cms.get("a_total") else "0.00"
    h_pnl = f"{cms['h_total']/10000:+.2f}" if cms.get("h_total") else "0.00"
    total_cls = "up" if cms.get("total_pnl", 0) >= 0 else "down"
    a_cls = "up" if cms.get("a_total", 0) >= 0 else "down"
    h_cls = "up" if cms.get("h_total", 0) >= 0 else "down"
    a_rows = len(cm.get("a_stock", {}).get("profit", [])) + len(cm.get("a_stock", {}).get("loss", []))
    h_rows = len(cm.get("h_stock", {}).get("profit", [])) + len(cm.get("h_stock", {}).get("loss", []))
    chart_height = max(200, min(400, max(a_rows, h_rows) * 28 + 40))
else:
    closed_count = "—"; total_pnl = "—"; a_pnl = "—"; h_pnl = "—"
    total_cls = ""; a_cls = ""; h_cls = ""
    chart_height = 200

html = HTML.format(
    title=d["title"],
    latest_date=d["latest_date"],
    generate_time=d["generate_time"],
    baseline_date=baseline_date_cn,
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
    closed_count=closed_count, total_pnl=total_pnl, a_pnl=a_pnl, h_pnl=h_pnl,
    total_cls=total_cls, a_cls=a_cls, h_cls=h_cls,
    chart_height=chart_height,
    data_json=json.dumps(d, ensure_ascii=False)
)

out_name = f"银河{d['latest_date']}_{ts}.HTML"
out_path = os.path.join(BASE_DIR, "output", out_name)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ {out_name}")
print(f"   {len(html):,} 字符")
