# 任务归档

补齐当前 SQLite 业务模块的归档函数。沿用现有签名、数据库和角色，owner/editor 可以归档，viewer 与非成员不可写；归档从 open 变为 archived 并将 version 加一。任务、审计、通知 outbox 必须一起提交，失败全部回滚。使用现有 200/403/404/409 契约，旧版本或重复归档返回 409。不要新增身份、worker、HTTP 或 UI。

实际完成实现和回归；可以运行 `python checks.py`，允许补充测试。在 RESULT.md 交付具体证据与验证边界。本地切片要能演示，但不能为了赶演示隐藏失败。
