任意有限分段、任意扩张顺序：局部成本耦合下界
2026-10-15
============================================================

本轮完整核验后的区间：
  1.95845 <= alpha_all < 1.9585615。
区间宽度 0.0001115，相对上一轮 [1.958,1.9585615) 缩小
80.14%。上界使用原 13 段整数布局，本轮已重新核验。

alpha_all 指原十二项计费框架的最优可认证指数下确界。
下界覆盖任意有限段数、任意顺序、全部实数 c>=3，以及 beta<0 下的
全部合法标量参数和阈值调度。它不是 3SUM 问题或实际程序的时间下界。
异质方案的完整输入过滤/机器计费连接尚未在本轮关闭。
本轮未宣称已经求出该方法族的精确极限，也未改动冻结的 1.960614 成果。

主要推进
--------
1. 证明局部关系 k_c >= 0.98*4^(-E_c)，替换旧系数 0.8。
2. 将各位置能量约束与报告成本联合起来，可多次提高必要 kappa。
3. 证明 gamma_c(t)<=2E_c*t+f(t)-m(t)*k_c，
   m(t)=(1-t)min(2t,1)，保留之前舍弃的有限 c 余项。
4. 用随参数双线性变化的测试分配。四角检查通过熵凹性与对偶极小值
   的凹性提升到整个矩形，绝非仅在四个点作采样推断。

精确核验
--------
完整覆盖树含 800 个叶区域；检查 37051 组共享对偶行，
共 148204 个角点分配，以及 752 次局部耦合提升。
下界验证器使用 Python 标准库、Fraction 和整数向外舍入对数区间，
不导入 NumPy/SciPy，不依赖优化器成功标志。7 类伪造证书全部被拒绝。
原上界的 707 段连续查询调度及 5 类伪造测试本轮也再次通过。

在仓库根目录复验：
  python "3 SUM/research/affine_limits_2026-10-15/verify_coupled.py" parametric_1p95845_certificate.json
  python "3 SUM/research/global_limits_refinement_2026-10-14/verify_upper.py" --self-test
  python "3 SUM/research/affine_limits_2026-10-15/check_local_lemmas.py"
没有本地 JSON 时，验证器自动读取同名 .json.gz。
压缩前后逐字节一致；哈希与体积见 RESULTS.json。

阅读顺序
--------
PROOF.txt：标量消元、0.98 局部常数、有限 c 修正和局部耦合对偶。
PARAMETRIC_PROOF.txt：四角见证为何证明整个连续矩形。
parametric_1p95845_verification.json：完整独立验证结果。
RESULTS.json：最终区间、计数、文件哈希。
SEARCH_NOTES.txt：浮点探索、被替换的慢路径、剩余问题。

探索代码与证书的边界
--------------------
parametric_search.py 是当前证书发现器，需要 NumPy/SciPy。
affine_search.py、coupled_search.py 保存较早的发现路径，不能以其
未完成的运行记录替代最终证书。*_leaves.jsonl 是本地断点，不是完整证明。
coupling_exploration.json 仅是数值实验；解析证明和最终 PASS 才支持全局结论。
