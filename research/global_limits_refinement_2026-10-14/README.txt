3SUM 任意异质布局：全局界继续推进（2026-10-14）
=================================================

最终已验证结果
--------------
任意有限分段、任意扩张顺序的最优可认证主指数 alpha 满足
  1.958 <= alpha < 1.9585615。
取方便表述的上界，则区间为 [1.958,1.958562)。
与上一轮 [1.9533,1.9586106) 相比，区间宽度缩小约 89%。
全布局的精确最优值仍未找到。

全局下界检查通过：18060 个叶区域（116 个空区域、202 个解析区域、
17742 个多深度对偶区域），18059 个二分节点，283808 条对偶约束。
上界和下界分别有五项、四项伪造证书拒绝测试，全部通过。

研究范围
--------
继续上一轮的“任意有限分段、任意扩张顺序”区间。
所有指数均针对既有十二项计费公式和盒子约束；不是实际耗时下界，
更不是 3SUM 问题的复杂性下界。保持 beta<0、固定盒子预算、前缀报告、
查询缺失比例<=1/2。完整算法过滤与 word-RAM 桥接 H2/H3 仍未关闭。

可复验文件
----------
GLOBAL_PROOF.txt：排序约简、正 kappa 约束、多深度对偶下界的完整推导。
upper_certificate.json / upper_verification.json：十三段整数布局，
  707 个调度区间，主成本最大值 <1.958561444087，目标指数 1.958562。
checkpoint_lower_certificate.json / checkpoint_lower_verification.json：
  已验证的阶段下界 1.9579；不依赖浮点优化器。
kappa_multidepth_fast_certificate.json / kappa_multidepth_fast_verification.json：
  已通过的 1.958 全局下界证书；验证结果文件记录完整检查计数。
SEARCH_NOTES.txt：探索方向、失败简化和下一步可用的连续形状方程。

从项目根目录复验（只需 Python 标准库）
--------------------------------------
  python "3 SUM/research/global_limits_refinement_2026-10-14/verify_upper.py" --self-test
  python "3 SUM/research/global_limits_refinement_2026-10-14/verify_multidepth.py" --fast
  python "3 SUM/research/global_limits_refinement_2026-10-14/check_arithmetic.py"

阶段下界可单独检查：
  python "3 SUM/research/global_limits_refinement_2026-10-14/verify_multidepth.py" --prefix checkpoint_lower

上界有五项伪造证书拒绝测试；下界有四项：虚假目标、覆盖缺失、
超出逐点预算的对偶权重、虚增 kappa。算术另与旧 48 项区间库做
120 个精确包含关系对照。下界原始 JSON 较大，这是完整覆盖证书。

生成与验证的区别
----------------
build_upper.py 和 build_fast_cover.py 使用 SciPy/NumPy 发现有理见证。
它们不属于可信验证步骤。浮点 LP/SLSQP 的最优性、成功标志和有限
采样都不能建立全局下界；最终验证器重新核验全部不等式和分割树。
重新生成树可能耗时较长；可直接验证已有证书。
先前较慢的搜索生成器保留为辅助代码，停止的搜索没有被当作完整证明。

下界证明使用的 16 个测试单元没有限制未知布局的段数。布局可以有
任意有限多个断点，且可穿过测试单元；不等式对它们逐点成立。

本轮确立的结构结论
------------------
1. 扩张率从小到大排序不会使同一框架的成本变差，因此可以无损排序。
2. 平均正成本 kappa >= (4/5)*4^(-E)，不能与平均编码成本 E 脱钩后置零。
3. 多个递归深度的盒子约束可组合成有理线性对偶，约束同一个未知布局。

未完成：全布局精确最优值、连续最优形状定理、H2/H3 的完整算法桥接。
上一轮九段布局的 [1.9586103,1.9586106) 只适用于原布局，不能作为
本轮十三段布局的下界。本轮使用的是覆盖整个方法族的全局证书。

仓库整理（2026-10-15）：两份大型 *_certificate.json 同时提供无损 .json.gz，Git 只保存压缩版，验证器自动回退读取。原始字节哈希见 compressed-certificates.json。本地已有的解压副本保持可用。
