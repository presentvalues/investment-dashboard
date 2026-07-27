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

# ── 2. 读取最新 Excel 持仓数据 ──
raw_holdings = pd.read_excel(latest_file, sheet_name="持仓数据", header=None)
print(f"持仓数据 shape: {raw_holdings.shape}")

# 按表头名称定位列（而非固定列号）
header = raw_holdings.iloc[0].tolist()
col_map = {}
for i, h in enumerate(header):
    if pd.notna(h):
        col_map[str(h).strip()] = i
print(f"列映射: 持有金额=col{col_map.get('持有金额')}, 当日盈亏=col{col_map.get('当日盈亏')}")

# 定位"汇总"行
summary_idx = None
for i in range(len(raw_holdings)):
    if str(raw_holdings.iloc[i, 0]).strip() == "汇总":
        summary_idx = i
        break

if summary_idx is None:
    print("⚠️ 未找到汇总行，回退到最后一行为汇总")
    summary_idx = len(raw_holdings) - 1

amt_col = col_map["持有金额"]
pnl_col = col_map["当日盈亏"]
market_value_c29 = float(raw_holdings.iloc[summary_idx, amt_col]) if pd.notna(raw_holdings.iloc[summary_idx, amt_col]) else 0
day_pnl_d29 = float(raw_holdings.iloc[summary_idx, pnl_col]) if pd.notna(raw_holdings.iloc[summary_idx, pnl_col]) else 0
print(f"汇总行(行{summary_idx+1}): 持有金额={market_value_c29:,.0f}, 当日盈亏={day_pnl_d29:,.0f}")

# 排除"汇总"行，仅保留数据行
data_rows = raw_holdings[raw_holdings.iloc[:, 0] != "汇总"].copy()
data_rows = data_rows.iloc[1:]  # 去掉标题行
print(f"持仓数据行（排除汇总）: {len(data_rows)} 条")

# ── 3. 持仓列表（按表头名称定位9列） ──
# 代码/名称/仓位占比/最新价/持有数量/持有金额/持有盈亏/持有盈亏率/持仓天数
holdings_cols = {
    "代码": 0, "名称": 1,
    "仓位占比": col_map.get("仓位占比", 16),
    "最新价": col_map.get("最新价", 20),
    "持有数量": col_map.get("持有数量", 17),
    "持有金额": col_map.get("持有金额", 2),
    "持有盈亏": col_map.get("持有盈亏", 9),
    "持有盈亏率": col_map.get("持有盈亏率", 10),
    "持仓天数": col_map.get("持仓天数", 18),
}
holdings_list = []
for _, row in data_rows.iterrows():
    try:
        h = {
            "code": str(row.iloc[holdings_cols["代码"]]),
            "name": str(row.iloc[holdings_cols["名称"]]),
            "weight": float(row.iloc[holdings_cols["仓位占比"]]) * 100 if pd.notna(row.iloc[holdings_cols["仓位占比"]]) else 0,
            "price": float(row.iloc[holdings_cols["最新价"]]) if pd.notna(row.iloc[holdings_cols["最新价"]]) else 0,
            "qty": int(float(row.iloc[holdings_cols["持有数量"]])) if pd.notna(row.iloc[holdings_cols["持有数量"]]) else 0,
            "market_value": float(row.iloc[holdings_cols["持有金额"]]) if pd.notna(row.iloc[holdings_cols["持有金额"]]) else 0,
            "hold_pnl": float(row.iloc[holdings_cols["持有盈亏"]]) if pd.notna(row.iloc[holdings_cols["持有盈亏"]]) else 0,
            "hold_pnl_rate": float(row.iloc[holdings_cols["持有盈亏率"]]) * 100 if pd.notna(row.iloc[holdings_cols["持有盈亏率"]]) else 0,
            "days": int(float(row.iloc[holdings_cols["持仓天数"]])) if pd.notna(row.iloc[holdings_cols["持仓天数"]]) else 0,
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

# ── 读取手动覆盖配置 ──
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
config = {}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    print(f"配置覆盖: {config}")

if config.get("market_value"):
    market_value_c29 = float(config["market_value"])
    print(f"  → 持仓市值覆盖: {market_value_c29:,.2f}")
if config.get("total_value"):
    total_value = float(config["total_value"])
    cash = total_value - market_value_c29
    print(f"  → 总市值覆盖: {total_value:,.2f}, 现金推算: {cash:,.2f}")
if config.get("cum_pnl") is not None:
    manual_cum_pnl = float(config["cum_pnl"])
    print(f"  → 累计总盈亏覆盖: {manual_cum_pnl:,.2f}")
else:
    manual_cum_pnl = None

# 提醒缺失的手动数据
missing = []
if not config.get("market_value"): missing.append("股票持仓市值")
if not config.get("total_value"): missing.append("总市值")
if config.get("cum_pnl") is None: missing.append("累计总盈亏")
if missing:
    print(f"\n⚠️ 缺少手动精确数据: {', '.join(missing)}")
    print("  → 已使用 Excel 自动提取值作为近似")
    print(f"  → 当前: 持仓市值={market_value_c29:,.0f}, 总市值={total_value:,.0f}, 累计总盈亏=—")
    print("  → 请在 config.json 中填写精确值后重新运行\n")

# ── 5. 合并所有已清仓数据 ──
all_closed = []
for date_str, fpath in excel_files:
    try:
        df = pd.read_excel(fpath, sheet_name="已清仓", header=0, dtype={"代码": str})
        all_closed.append(df)
    except: pass

closed_df = pd.concat(all_closed, ignore_index=True) if all_closed else pd.DataFrame()
if not closed_df.empty:
    closed_df = closed_df.drop_duplicates(subset=["代码","清仓日期"] if "清仓日期" in closed_df.columns else ["代码"])
print(f"已清仓合并: {len(closed_df)} 条")

# 已清仓总盈亏 = 总盈亏列求和
closed_total_pnl = 0
pnl_col_name = None
for c in closed_df.columns:
    if "总盈亏" in str(c):
        pnl_col_name = c
        break
if pnl_col_name:
    closed_total_pnl = closed_df[pnl_col_name].sum()
    print(f"已清仓总盈亏: {closed_total_pnl:,.2f}")
else:
    print("⚠️ 未找到总盈亏列")

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

# ── 7.5 已清仓盈亏合并分析（按代码合并，A/H分类，盈亏前5）──
closed_merged = {"summary": {}, "a_stock": [], "h_stock": []}
if not closed_df.empty and pnl_col_name:
    # 只用最新 Excel 的已清仓数据（避免跨文件重复）
    latest_closed = pd.read_excel(latest_file, sheet_name="已清仓", header=0, dtype={"代码": str})
    # 按代码+名称分组求和
    grp = latest_closed.groupby(["代码", "名称"])[pnl_col_name].sum().reset_index()
    grp.columns = ["code", "name", "pnl"]
    # A/H分类：6位代码=A股，5位代码=港股
    a_list, h_list = [], []
    for _, r in grp.iterrows():
        code_str = str(r["code"])
        entry = {"code": code_str, "name": str(r["name"]), "pnl": round(float(r["pnl"]), 2)}
        if len(code_str) == 6:
            a_list.append(entry)
        else:
            h_list.append(entry)
    # 汇总
    all_pnl = sum(x["pnl"] for x in a_list + h_list)
    a_total = sum(x["pnl"] for x in a_list)
    h_total = sum(x["pnl"] for x in h_list)
    stock_count = len(a_list) + len(h_list)
    closed_merged["summary"] = {
        "count": stock_count, "total_pnl": round(all_pnl, 2),
        "a_total": round(a_total, 2), "h_total": round(h_total, 2),
    }
    # 取盈亏前5
    def top5_profit_loss(items):
        profit = sorted([x for x in items if x["pnl"] > 0], key=lambda x: -x["pnl"])[:5]
        loss = sorted([x for x in items if x["pnl"] < 0], key=lambda x: -x["pnl"])[:5]  # 亏损低→高
        return {"profit": profit, "loss": loss}
    closed_merged["a_stock"] = top5_profit_loss(a_list)
    closed_merged["h_stock"] = top5_profit_loss(h_list)
    print(f"已清仓合并: {stock_count}只, 总盈亏={all_pnl:,.2f}, A股={a_total:,.2f}, 港股={h_total:,.2f}")

# ── 8. 账户收益率序列 ──
return_series = []
if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE) as f:
        idx_cfg = json.load(f)
    baseline_date = idx_cfg.get("baseline_date")
    baseline_tv = idx_cfg.get("baseline_total_value")
    idx_series = idx_cfg.get("series", [])
    if baseline_date and baseline_tv and idx_series:
        # 计算每日收益率（基准日为0%，总市值来源于 index_data.json 中的截图数据）
        for item in idx_series:
            date_str = item["date"]
            tv = item.get("total_value")
            account_ret = round((tv / baseline_tv - 1) * 100, 2) if tv else None
            base_sh = idx_series[0]["shanghai"]
            base_csi = idx_series[0]["csi300"]
            base_cx = idx_series[0].get("chinext")
            sh_ret = round((item["shanghai"] / base_sh - 1) * 100, 2)
            csi_ret = round((item["csi300"] / base_csi - 1) * 100, 2)
            cx_ret = round((item["chinext"] / base_cx - 1) * 100, 2) if base_cx and item.get("chinext") else None
            return_series.append({
                "date": date_str,
                "account": account_ret,
                "shanghai": sh_ret,
                "csi300": csi_ret,
                "chinext": cx_ret,
                "total_value": tv,
            })
        print(f"收益率序列: {len(return_series)} 个数据点")

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
        "cum_pnl": round(manual_cum_pnl, 2) if manual_cum_pnl is not None else None,
        "closed_total_pnl": round(closed_total_pnl, 2),   # 空着
        "account_value": None,
        "time_weighted_return": None,
        "net_deposit": round(total_net_deposit, 2),
    },
    "holdings": holdings_list,
    "closed_analysis": closed_analysis,
    "closed_merged": closed_merged,
    "cum_pnl_seq": cum_pnl_seq,
    "yearly_data": yearly_data,
    "return_series": return_series,
}

with open(os.path.join(OUTPUT_DIR, "data.json"), "w") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
print(f"✅ data.json 已生成")
