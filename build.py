#!/usr/bin/env python3
# build.py — 辰影的自由之路持仓每日盈亏看板 构建脚本
# 用法: python3 build.py

import json, os, sys, glob, re
from datetime import datetime
from collections import defaultdict
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
INDEX_FILE = os.path.join(BASE_DIR, "index_data.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 1. 扫描 raw/ 下所有 Excel ──
def scan_excels():
    files = glob.glob(os.path.join(RAW_DIR, "银河*.xlsx"))
    result = []
    for f in files:
        m = re.search(r'(\d{4}-\d{2}-\d{2})', os.path.basename(f))
        if m: result.append((m.group(1), f))
    result.sort()
    return result

excel_files = scan_excels()
print(f"发现 {len(excel_files)} 个 Excel 文件")
for d, f in excel_files:
    print(f"  {d}: {os.path.basename(f)}")
if not excel_files:
    print("无 Excel 文件，退出"); sys.exit(1)

latest_date = excel_files[-1][0]
latest_file = excel_files[-1][1]

# ── 2. 读取最新 Excel 持仓数据（header=None 精确取C29/D29） ──
raw_holdings = pd.read_excel(latest_file, sheet_name="持仓数据", header=None)
print(f"持仓数据 shape: {raw_holdings.shape}")

# C29 = row 28 (0-indexed), col 2 = 持有金额
# D29 = row 28 (0-indexed), col 3 = 当日盈亏
summary_row = raw_holdings.iloc[28]  # Excel row 29
market_value_c29 = float(summary_row.iloc[2]) if pd.notna(summary_row.iloc[2]) else 0
day_pnl_d29 = float(summary_row.iloc[3]) if pd.notna(summary_row.iloc[3]) else 0
print(f"C29 持仓市值: {market_value_c29:,.0f}")
print(f"D29 当日盈亏: {day_pnl_d29:,.0f}")

# 排除"汇总"行，仅保留数据行（row 1..27, col 0 != "汇总"）
data_rows = raw_holdings[raw_holdings.iloc[:, 0] != "汇总"].copy()
data_rows = data_rows.iloc[1:]  # 去掉标题行(row 0)
print(f"持仓数据行（排除汇总）: {len(data_rows)} 条")

# ── 3. 持仓列表（仅9列：代码/名称/仓位占比/最新价/持有数量/持有金额/持有盈亏/持有盈亏率/持仓天数） ──
holdings_list = []
for _, row in data_rows.iterrows():
    try:
        h = {
            "code": str(row.iloc[0]),
            "name": str(row.iloc[1]),
            "weight": float(row.iloc[16]) * 100 if pd.notna(row.iloc[16]) else 0,   # 仓位占比→百分比
            "price": float(row.iloc[20]) if pd.notna(row.iloc[20]) else 0,           # 最新价
            "qty": int(float(row.iloc[17])) if pd.notna(row.iloc[17]) else 0,        # 持有数量
            "market_value": float(row.iloc[2]) if pd.notna(row.iloc[2]) else 0,      # 持有金额
            "hold_pnl": float(row.iloc[9]) if pd.notna(row.iloc[9]) else 0,          # 持有盈亏
            "hold_pnl_rate": float(row.iloc[10]) * 100 if pd.notna(row.iloc[10]) else 0,  # 持有盈亏率
            "days": int(float(row.iloc[18])) if pd.notna(row.iloc[18]) else 0,       # 持仓天数
        }
        holdings_list.append(h)
    except Exception as e:
        print(f"  ⚠️ 跳过行: {e}")

holdings_list.sort(key=lambda x: x["weight"], reverse=True)
print(f"持仓列表: {len(holdings_list)} 条")

# ── 4. 解析所有 Excel 的交易记录 ──
all_trades = []
for date_str, fpath in excel_files:
    try:
        df = pd.read_excel(fpath, sheet_name="交易记录", header=None)
        df = df.iloc[1:]
        df.columns = ["成交日期","成交时间","代码","名称","交易类别","成交数量","成交价格","发生金额","成交金额","费用","备注"]
        all_trades.append(df)
    except Exception as e:
        print(f"⚠️ 解析 {date_str} 交易记录失败: {e}")

trades = pd.concat(all_trades, ignore_index=True)
trades["成交日期"] = pd.to_datetime(trades["成交日期"], errors="coerce")
trades["发生金额"] = pd.to_numeric(trades["发生金额"], errors="coerce")
trades = trades.dropna(subset=["成交日期"]).sort_values(["成交日期","成交时间"])
print(f"交易记录合并: {len(trades)} 条")

# 净入金
net_deposits = []
for _, t in trades.iterrows():
    if isinstance(t["交易类别"], str) and "银行转证券" in t["交易类别"]:
        net_deposits.append(t["发生金额"])
total_net_deposit = sum(net_deposits)
print(f"累计净入金: {total_net_deposit:,.2f}")

# 现金 = 最新国债逆回购行的发生金额（绝对值）
repo_rows = trades[trades["交易类别"].str.contains("回购", na=False)]
latest_repo = repo_rows.iloc[-1]
cash = abs(float(latest_repo["发生金额"]))
total_value = market_value_c29 + cash
print(f"现金(最新回购): {cash:,.0f}")
print(f"总市值: {total_value:,.0f}")

# ── 5. 合并所有已清仓数据 ──
all_closed = []
for date_str, fpath in excel_files:
    try:
        df = pd.read_excel(fpath, sheet_name="已清仓", header=0)
        all_closed.append(df)
    except: pass

closed_df = pd.concat(all_closed, ignore_index=True) if all_closed else pd.DataFrame()
if not closed_df.empty:
    closed_df = closed_df.drop_duplicates(subset=["代码","清仓日期"] if "清仓日期" in closed_df.columns else ["代码"])
print(f"已清仓合并: {len(closed_df)} 条")

# ── 6. 已清仓分析 ──
closed_analysis = {"A股": [], "港股": []}
closed_daily = []  # 清仓盈亏按日期
if not closed_df.empty:
    for _, row in closed_df.iterrows():
        code_val = str(row.get("代码", ""))
        name_val = str(row.get("名称", ""))
        pnl_val = float(row.get("盈亏金额", 0)) if pd.notna(row.get("盈亏金额", np.nan)) else 0
        close_date = row.get("清仓日期", None)
        # A/H 判断
        market = "A股"
        if code_val.isdigit() and len(code_val) == 5: market = "港股"
        closed_analysis[market].append({
            "code": code_val, "name": name_val,
            "pnl": round(pnl_val, 2)
        })
        if close_date and pd.notna(close_date):
            closed_daily.append({"date": str(close_date)[:10], "pnl": pnl_val})

# 按日聚合
pnl_by_date = defaultdict(float)
for item in closed_daily:
    pnl_by_date[item["date"]] += item["pnl"]
cum_pnl_seq = []
running = 0
for d in sorted(pnl_by_date.keys()):
    running += pnl_by_date[d]
    cum_pnl_seq.append({"date": d, "cum_pnl": round(running, 2)})

# ── 7. 年度盈亏 ──
yearly_pnl = defaultdict(float)
if not closed_df.empty:
    for _, row in closed_df.iterrows():
        cd = row.get("清仓日期", None)
        if cd and pd.notna(cd):
            y = str(cd)[:4]
            pnl_v = float(row.get("盈亏金额", 0)) if pd.notna(row.get("盈亏金额", np.nan)) else 0
            yearly_pnl[y] += pnl_v
yearly_data = [{"year": y, "pnl": round(p, 2)} for y, p in sorted(yearly_pnl.items())]

# ── 8. 加载指数数据 ──
with open(INDEX_FILE) as f:
    index_raw = json.load(f)

def normalize_index(data, start_date="2024-01-02"):
    dates = sorted(data.keys())
    if start_date not in data: start_date = dates[0]
    base = data[start_date]
    return {d: round(v / base * 100, 2) for d, v in data.items()}

index_norm = {name: normalize_index(index_raw[name]) for name in ["沪深300","创业板指","上证指数"] if name in index_raw}

# ── 9. 组装 JSON ──
day_pnl_rate = round(day_pnl_d29 / (market_value_c29 - day_pnl_d29) * 100, 2) if (market_value_c29 - day_pnl_d29) != 0 else 0

output_data = {
    "title": "辰影的自由之路持仓每日盈亏看板",
    "generate_time": (datetime.now() + __import__('datetime').timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
    "latest_date": latest_date,
    "summary": {
        "market_value": round(market_value_c29, 2),
        "day_pnl": round(day_pnl_d29, 2),
        "day_pnl_rate": day_pnl_rate,
        "cash": round(cash, 2),
        "total_value": round(total_value, 2),
        "cum_pnl": None,   # 空着
        "account_value": None,
        "time_weighted_return": None,
        "net_deposit": round(total_net_deposit, 2),
    },
    "holdings": holdings_list,
    "closed_analysis": closed_analysis,
    "cum_pnl_seq": cum_pnl_seq,
    "yearly_data": yearly_data,
    "index_normalized": index_norm,
}

with open(os.path.join(OUTPUT_DIR, "data.json"), "w") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
print(f"✅ data.json 已生成")
