# 原始证据

每个 `<client>-<project>` 目录保存该次运行的直接证据：

- `diff.patch`：相对 base commit 的完整改动（应为空或只含 src/）
- `git-status.txt`：工作区状态
- `pytest.txt`：验收测试的完整输出

## 会话 ID（用于回溯客户端侧 usage）
| client | project | session |
|---|---|---|
| opencode | werkzeug | `ses_e93692f86ffeCAMqhNeKgRcd8d` |
| opencode | pytest | `ses_e935e4448ffe0NjF7iys0MajCF` |
| pi | werkzeug | `results/pi-sessions/2026-10-24T06-27-36-560Z_01a16c97-e5f0-76b0-bb6b-7466393c1cb5.jsonl` |
| pi | pytest | `results/pi-sessions/2026-10-24T06-39-46-993Z_01a16ca3-0b30-7122-9fb5-c55419a88471.jsonl` |
| hermes | werkzeug | `local-03b7566358dd839e5a8e144716f55f6448d2c2a7f728d16f2285a79d6cce88d4` |
| hermes | pytest | `local-476f9037c23d163d28c3a53d9d81b691ca62a57dc2861853c8b780acac652b25` |

opencode 回溯：`cd work/opencode-<project> && opencode session export <id>`
Hermes 回溯：`sqlite3 ~/.hermes/state.db "select * from session_model_usage where session_id='<id>'"`
