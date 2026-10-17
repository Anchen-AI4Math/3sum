# 3SUM 研究与成果

本目录汇总 2026 年 10 月的 3SUM 研究材料。**本次最终成果是确定性 word-RAM 的 O(n^1.960614) 完整形式化，已保存 Prove2Me 完成回执和 Big O 官方验证通过的证据。**

请从 [2026-10-15 最终成果归档](results/2026-10-15_1p960614/README.md) 开始阅读，包含中文说明、固定公开提交的完整源码、原始解析证书、平台验收材料、两张用户截图及离线哈希校验工具。

技术报告与配套证明材料已于 **2026-10-16** 在 Zenodo 公开发布，版本 **1.0.0**，DOI：[10.5281/zenodo.23408567](https://doi.org/10.5281/zenodo.23408567)。[本地发布记录](submissions/zenodo_1p960614/PUBLICATION.txt)保存正式链接、引用信息和附件核对结果；平台资源类型为 Report，属于技术报告公开归档。

## 按阶段查找

| 阶段 | 位置 | 使用说明 |
| --- | --- | --- |
| 最终成果：1.960614 | [results/2026-10-15_1p960614/](results/2026-10-15_1p960614/README.md) | 完整机器定理、平台图闭合及官方验证的归档入口 |
| 原 v3 解析证书 | [3sum_certificate_1p960614_v3/](3sum_certificate_1p960614_v3/3sum_certificate_v3/README.md) | 四次/八次开关、参数、整数调度与固定模型极限；其 README 的未形式化说明属于早期阶段 |
| 初始研究 | [3sum_exponent_research_2026-10-13/](research/3sum_exponent_research_2026-10-13/) | 早期研究包及对应 ZIP |
| 继续研究 | [continuation_2026-10-14/](research/continuation_2026-10-14/) | 全局参数证书、推导及研究评估 |
| 固定数值纸面证书：1.9593 | [certificate_1p9593_2026-10-16/](research/certificate_1p9593_2026-10-16/README.txt) | 两段异质布局；补齐原输入、YES质量保护和操作账本的纸面证明，附独立数值及有限集成复验；尚非Lean机器定理 |
| 局部耦合极限精化 | [affine_limits_2026-10-15/](research/affine_limits_2026-10-15/README.txt) | 任意有限异质布局的可认证指数区间收紧至 [1.95845, 1.9585615)；完整有理证书，异质方案的端到端连接仍待完成 |
| 全局极限精化 | [global_limits_refinement_2026-10-14/](research/global_limits_refinement_2026-10-14/README.txt) | 进一步的模型极限研究 |
| 异质模型研究 | [heterogeneous_limits_2026-10-14/](research/heterogeneous_limits_2026-10-14/README.txt) | 异质方案与模型分析 |
| 算法搜索 | [algorithm_search_2026-10-14/](research/algorithm_search_2026-10-14/README.txt) | 搜索过程与阶段结果 |
| 早期 Hexagon 准备包 | [hexagon_submission/](submissions/hexagon_1p999017/README_提交说明.txt) | 主标题为 1.999017 的投稿准备材料；不等同于本次 1.960614 最终成果或已发表论文 |
| 审计参考材料 | [audit_sources/](references/audit_sources/) | 原始参考源；[audit/](audit/) 中的审计报告和脚本按生成时的版本理解 |

## 状态与复验

最终状态以成果目录的 `evidence/mission-completion.json` 为准；早期报告、运行日志和原始证书保持原样，便于追溯。用户提供的 Big O 截图显示当时排名第一，官方保存回执同时标记 `site_eligible_for_record: false`，两类事实在成果说明中分别记录。

在本目录执行离线完整性校验：

```powershell
python results/2026-10-15_1p960614/verify_archive.py
```

该命令校验归档内容与保存回执，不重跑 Lean。完整复验范围见 [REPRODUCE.md](results/2026-10-15_1p960614/REPRODUCE.md)。原 Prove2Me 任务工作目录仍在 `D:\users\self_projects\prove2me_workspace\missions\3sum-1960614`。

## 目录约定

`results/` 保存冻结的最终成果，`research/` 保存各阶段研究，`audit/` 保存独立复核，`references/` 保存引用源码及平台资料，`archives/` 保留原始输入 ZIP，`submissions/` 保存投稿准备材料。原 v3 证书目录保持原路径，供 prove2me_workspace 引用。

文件迁移逐一校验内容哈希，映射见 [organization-2026-10-15.json](organization-2026-10-15.json)。历史材料中旧路径按迁移映射查找；冻结成果目录及其校验清单保持不变。

全局极限研究的两份大 JSON 以 `.json.gz` 无损压缩保存，`verify_multidepth.py` 自动读取压缩版；本地已有的解压副本不纳入 Git。原始/压缩字节数和 SHA-256 见 [压缩证书清单](research/global_limits_refinement_2026-10-14/compressed-certificates.json)。`submissions/hexagon_1p999017/build/` 是可再生的本地编译产物，也不纳入 Git。
