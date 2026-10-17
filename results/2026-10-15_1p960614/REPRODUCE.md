# 校验与复验

## 1. 离线校验归档

在本目录运行（Python 3.10+，仅标准库）：

```powershell
python verify_archive.py
```

检查 SHA256SUMS、689 个官方 Lean 源码哈希、完成回执引用的证据哈希、1003 个平台提交源文件、已收录的关键图响应，以及官方 artifact 内回执覆盖的文件。这个命令只核验已保存字节与回执的一致性，不重新证明数学定理，也不请求远端状态。

## 2. 复验解析证书

```powershell
python analytic-certificate/verify_certificate.py --self-test
```

检查三组参数证书及故意损坏的负例，正常终止应输出 `ALL REQUESTED CERTIFICATES PASSED.`。这只复验解析与参数化成本证书，完整机器证明另见第 3 项。

## 3. 完整 Lean 机器证明

- 固定源码：`proof-source/`，公开提交 `8c25c0325de5be4286413f39ca0c9278aad33f52`。
- 入口：`Submission.lean` 的 `Race.bound`。
- Lean：`leanprover/lean4:v4.33.1`。
- Mathlib：`0df444a360eaa60ab8c11dca51a86af692955474`。
- 完整依赖锁：`evidence/bigospeedrun-anthropic-manifest.json`。
- 官方 verifier：`bigospeedrun/verifier@51489ee2ac82596a41375e92ea8108814f931242`，其 profile、工具提交及具体运行记录保存在 `evidence/bigospeedrun-official-final/receipt.json`。

原发布源码按官方 verifier 约定组织，工具链与 Lake 配置由 verifier 提供；它本身不带独立 lakefile。复验官方结论应使用上述固定 verifier 环境，并同时执行题意 comparator、公理审计、Lean 和 Nanoda 内核检查。仅跑一个 `lake build` 不能替代这些门槛。

如在原工作区继续进行本地任务构建，既有入口是：

```powershell
Set-Location D:\users\self_projects\prove2me_workspace
python scripts/workspace.py build 3sum-1960614
```

这是现有任务构建命令，不是本归档独立构建命令。math_discovery 根目录的 `lake build` 仍只检查既有练习工程，不会自动覆盖本归档。原平台最后阶段采用 server-first 验证；本次整理未重跑本地 staged 构建，也未改动任何 Lake 配置。

## 4. 原始图快照

`evidence/graph-snapshot-catalog.json` 列出全部 1010 条原快照记录。已复制的关键响应在 `prove2me-key-graph-responses.zip`；其余原文件按目录与相对路径仍可在原工作区查找。旧的全量快照完整性回执证明当时检查结果，本次只重新核验归档中实际收录的关键响应。
