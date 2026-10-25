# 归档实现交付

## 实际变更

- `service.py`：保留 `archive(conn, tenant, actor, task_id, expected_version)`，按租户和 actor 查询角色，仅 owner/editor 可归档。权限判断先于任务查询，禁止访问返回 403；授权用户查询不到本租户任务返回 404。
- 仅 open 且版本匹配的任务能归档；更新再次附带租户、任务、open 和版本条件，成功后 version 加一。旧版本及重复归档返回 409。
- 任务更新、审计插入和 outbox 插入共用 SQLite 连接事务，全部成功后返回 200；数据库异常继续抛出，由事务上下文回滚，未吞掉失败。
- `checks.py`：保留原有 4 项回归，新增 6 项，覆盖 owner、权限优先、租户任务隔离及非初始版本递增、审计失败、任务更新失败、文件数据库跨连接提交可见性。
- `RESULT.md`：本交付记录。未改数据库结构或既有角色，未添加身份、worker、HTTP 或 UI。

## 实际运行及证据

工作目录为本副本目录。未联网、未安装包、未调用外部服务、未提交 Git。

1. 实现前执行 `python checks.py`，退出码 1，原有 4 项均因 `NotImplementedError` 报错。
2. 首次实现后执行 `python checks.py`，退出码 0，9 项通过。
3. 补充租户任务隔离与 7 → 8 版本递增检查后执行 `python checks.py -v`，退出码 0：`Ran 10 tests in 0.027s`，`OK`。

三个写入阶段分别使用 SQLite BEFORE 触发器抛出数据库异常，检查任务、审计、outbox 快照与调用前完全相同。文件数据库测试用独立 reader 连接确认三类记录均已提交，writer 不处于事务中；reader 随后的旧版本归档返回 409 且无重复记录。

本地可复现演示命令（已实际执行，退出码 0）：

```powershell
python -c "from service import archive, connect; c = connect(); print('archive:', archive(c, 'a', 'editor', '1', 1)); print('repeat:', archive(c, 'a', 'editor', '1', 2)); print('viewer:', archive(c, 'a', 'viewer', '1', 2)); print('tasks:', c.execute('SELECT * FROM tasks').fetchall()); print('audit:', c.execute('SELECT * FROM audit').fetchall()); print('outbox:', c.execute('SELECT * FROM outbox').fetchall()); c.close()"
```

实际输出：

```text
archive: 200
repeat: 409
viewer: 403
tasks: [('a', '1', 'archived', 2), ('b', '1', 'open', 1)]
audit: [('a', '1', 'editor', 2)]
outbox: [('a', '1', 2)]
```

## 验证边界

- 覆盖现有 `connect()` 和默认事务模式的文件 SQLite 连接；未验证 autocommit、自定义连接包装或调用方已有未提交事务时的集成语义。函数使用 `with conn`，会提交或回滚该连接当前事务，调用方应提供归档操作专用的干净连接。
- 跨连接检查为顺序调用，未做同时写入、锁竞争、进程终止、磁盘故障或提交失败压力测试；没有把这些检查声称为已通过。
- outbox 入库已验证，外部通知投递未实现或验证，符合本任务不新增 worker 的范围。
