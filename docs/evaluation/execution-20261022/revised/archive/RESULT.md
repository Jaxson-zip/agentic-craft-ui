# SQLite 任务归档交付

状态：本地实现与回归 passed；未运行项见下文。仅修改本 archive 副本，沿用原函数签名、表结构、角色与返回码；没有新增身份、worker、HTTP 或 UI。

## 实现

- `service.py`：在 SQLite 事务中读取当前 tenant 的成员角色和任务；仅 owner/editor 可写。非成员/viewer 返回 403，授权成员查不到任务返回 404。
- 任务必须为 open 且 version 等于 expected_version，否则返回 409；更新带 tenant/id/state/version 条件，变为 archived、version 加一。
- 同一事务写入任务、带 actor 的 audit 和 outbox，三者成功提交后才返回 200。数据库写入异常继续抛出，由连接事务上下文回滚；未把数据库错误伪装成业务成功。
- 无既有事务时使用 BEGIN IMMEDIATE，在读取权限与任务之前取得写锁。若调用者已有事务，沿用该事务；连接上下文会提交或回滚它，因此调用者不应把无关待提交工作混在同一连接事务中。
- `checks.py`：保留原有 4 项测试，补充 owner、审计写入失败及恢复、文件数据库第二连接读取已提交结果的 3 项回归。

## 实际命令与证据

运行目录：`G:\skill\agentic-craft-ui-evaluation\optimization-2026-10-22\revised\archive`。使用系统现有 Python、sqlite3/unittest/tempfile 标准库；未联网、未安装包。

| 检查 | 状态 | 结果 |
| --- | --- | --- |
| 修改前 `python checks.py` | failed（基线） | 4 项测试均因 NotImplementedError 失败，退出码 1 |
| 补测后、实现前 `python checks.py` | failed（红灯） | 7 项测试均因 NotImplementedError 失败，退出码 1 |
| 实现后 `python checks.py` | passed | Ran 7 tests，OK，退出码 0 |
| `python -m unittest -v checks` | passed | 7 项具名回归全部 ok，退出码 0 |
| 下方本地演示（PowerShell here-string 通过管道传给 `python -`） | passed | 实际打印权限、归档结果及三表数据，退出码 0 |

测试覆盖：owner/editor 权限、viewer/非成员拒绝、tenant 隔离、404、旧版本 409、重复归档 409、无副作用拒绝、outbox 失败回滚任务与审计、audit 失败回滚并恢复重试，以及三表真实提交后被另一连接读到。

可复现演示：

```powershell
@'
from service import archive, connect
conn = connect()
print('viewer:', archive(conn, 'a', 'viewer', '1', 1))
print('archive:', archive(conn, 'a', 'editor', '1', 1))
print('task:', conn.execute("SELECT * FROM tasks WHERE tenant='a' AND id='1'").fetchone())
print('audit:', conn.execute('SELECT * FROM audit').fetchall())
print('outbox:', conn.execute('SELECT * FROM outbox').fetchall())
print('duplicate:', archive(conn, 'a', 'editor', '1', 2))
conn.close()
'@ | python -
```

实际输出：

```text
viewer: 403
archive: 200
task: ('a', '1', 'archived', 2)
audit: [('a', '1', 'editor', 2)]
outbox: [('a', '1', 2)]
duplicate: 409
```

## 验证边界

- not-run：同时竞争的多线程/多进程写入压力、锁超时、进程崩溃及硬件故障恢复。第二连接测试证明提交可见和后续旧版本冲突，不等于并发压力或崩溃恢复测试。
- not-run：调用者已有事务与特殊 SQLite autocommit 配置的额外兼容性测试；本次使用现有 connect() 默认配置和默认文件连接。
- not-applicable：UI、浏览器、HTTP、通知 worker 及实际通知投递；本任务仅写入现有 outbox。
- 没有读取其他评估条件或结果，也未读取禁止的执行说明；未调用外部服务、未提交 Git。

变更文件：`service.py`、`checks.py`、`RESULT.md`。
