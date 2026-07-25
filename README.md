# 辰影的自由之路 — 持仓每日盈亏看板

基于银河证券导出的 Excel 持仓数据，自动生成交互式 HTML 看板。

## 数据流程

```
银河证券导出 Excel（银河YYYY-MM-DD.xlsx）
         ↓ 放入 raw/
    build.py        ← 解析持仓/交易/清仓数据
         ↓
    data.json
         ↓
  generate_html.py  ← 生成 ECharts 图表 + 表格
         ↓
  银河YYYY-MM-DD_HHMMSS.HTML   ← 上传知识库
```

## 目录结构

```
├── raw/                 ← 每日 Excel 原始文件（不入库）
├── output/              ← 生成文件（不入库）
├── index_data.json      ← 三大指数历史K线（搜狐API拉取）
├── build.py             ← 数据解析：持仓/交易/清仓 → JSON
├── generate_html.py     ← HTML生成：JSON → 内嵌 ECharts 看板
├── daily_update.sh      ← 一键更新脚本
├── .gitignore
└── README.md
```

## 快速开始

```bash
# 1. 将银河证券导出的 Excel 放入 raw/
# 2. 执行构建
python3 build.py && python3 generate_html.py

# 3. 上传到知识库
python3 /sandbox/workspace/skills/ima-knowledge/scripts/upload_file.py \
  --file-path output/银河*.HTML \
  --knowledge-base-id iC7b7Bpw5o4239yQloePDeAdgp34funOnyBGJNTaS0k=
```

## HTML 看板功能

- 📊 顶部汇总卡片（持仓市值/当日盈亏）
- 📋 当前持仓表格（9列：代码/名称/仓位占比/最新价/持有数量/持有金额/持有盈亏/持有盈亏率/持仓天数）
- 📈 累计已实现收益曲线
- 📉 三大指数对比图（沪深300/创业板指/上证指数，搜狐API）
- 📦 已清仓盈亏分析（A股+港股柱状图）
- 📅 历史年度盈亏（柱+折线双轴）

## 后续计划

- [ ] 累计收益K线图（含EMA12/26/零轴/清仓事件标注）
- [ ] 资金构成堆叠面积图（股票/基金/债券/现金）
- [ ] 实盘周记自动生成（HTML→PNG→公众号）
- [ ] 历史每日 Excel 串联净值
