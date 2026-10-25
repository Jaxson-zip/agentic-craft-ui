# 日期筛选修复结果

已修复 UTC 存储时间与 UTC+08:00 日历日期不一致造成的漏单、错单。`for_day(rows, selected_day)` 接口、返回原始行及输入顺序保持不变。

## 根因与修改

原实现比较 `row['at'][:10]`，将存储字符串中的日期直接当作本地日期。现在在 `ledger.py` 中构造 UTC+08:00 所选日期零点至次日零点的左闭右开区间，解析 `Z` 或显式偏移的时间戳后按实际时间比较。使用 Python 标准库，没有安装依赖。

## 实际执行与证据

工作目录：本副本目录。

| 阶段 | 实际命令 | 状态与结果 |
| --- | --- | --- |
| 修复前复现 | `python checks.py` | failed，退出码 1，3 个检查全部失败；零点边界实际 `[2, 3]`，期望 `[1, 2]`；显式偏移漏一行；跨月漏单。 |
| 修复前留存 | `python checks.py 2>&1 \| Out-File -LiteralPath '.\before-checks.txt' -Encoding utf8; exit $LASTEXITCODE` | failed，退出码 1，完整失败输出已在修改前保存。 |
| 修复后回归 | `python checks.py 2>&1 \| Tee-Object -FilePath '.\after-checks.txt'; exit $LASTEXITCODE` | passed，退出码 0，3 个原有检查全部通过。 |

回归覆盖本地零点纳入、次日零点排除、带不同时区偏移的等价时间、输入顺序、空列表及跨月边界。未改动 `checks.py` 的断言。

## 变更文件

- `ledger.py`：修复日期筛选逻辑。
- `before-checks.txt`：修改前的可复现失败输出。
- `after-checks.txt`：修改后的通过输出。
- `RESULT.md`：本交付说明。

## 未验证项与适用边界

- not-run：真实界面与持久化账本联调；副本仅提供筛选函数与单元检查。
- not-run：非法日期、非法时间戳、无时区时间戳的输入策略；当前验证范围为所提供的有效日期及带 `Z`/显式时区偏移的数据。
- not-applicable：UI 重设计、生产构建与部署；本任务未涉及这些内容。

未联网、未安装包、未调用外部服务、未提交 Git，所有写入均在当前副本内。
