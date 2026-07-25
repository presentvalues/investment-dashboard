#!/bin/bash
# daily_update.sh — 每日更新：放入原始 Excel 后执行
# 用法: bash daily_update.sh
# 前提: raw/ 目录下有最新 银河YYYY-MM-DD.xlsx

set -e
cd "$(dirname "$0")"

echo "=== 1. 更新指数数据 ==="
python3 - <<'PY'
import json, subprocess
indices = {"沪深300":"zs_000300","创业板指":"zs_399006","上证指数":"zs_000001"}
data = {}
for name, code in indices.items():
    url = f"https://q.stock.sohu.com/hisHq?code={code}&start=20240101&end=20260730"
    r = subprocess.run(["curl","-s",url], capture_output=True, text=True)
    d = json.loads(r.stdout)
    data[name] = {row[0]: float(row[2]) for row in d[0]["hq"]}
    print(f"  {name}: {len(data[name])} 条")
with open("index_data.json","w") as f:
    json.dump(data, f, ensure_ascii=False)
print("  指数更新完成")
PY

echo ""
echo "=== 2. 构建数据 JSON ==="
python3 build.py

echo ""
echo "=== 3. 生成 HTML ==="
python3 generate_html.py

echo ""
LATEST=$(ls -t output/银河*.HTML | head -1)
echo ""
echo "=== 4. 输出文件 ==="
ls -lh "$LATEST"
echo ""
echo "下一步：手动上传 $LATEST 到知识库"
echo "   python3 /sandbox/workspace/skills/ima-knowledge/scripts/upload_file.py --file-path $(pwd)/$LATEST --knowledge-base-id iC7b7Bpw5o4239yQloePDeAdgp34funOnyBGJNTaS0k="
