3SUM：继续优化与方法下限，2026-10-14
============================================================

本轮得到三个不同层次的结果：

1. 条件上界从上一轮 1.95923 推进到 1.958611。
   九种整数扩张率、703 段有理调度，实际验证的主成本最大值
   <1.958610566516。上界的过滤/word-RAM 连接义务 H2、H3 仍未关闭。

2. 固定这组九段布局，允许任意连续标量参数和阈值调度，
   最优可认证主指数已夹在 [1.9586103,1.9586106)，宽度 3e-7。

3. 放开布局，允许任意有限段数、任意扩张顺序、甚至实数 c>=3，
   当前同一计费框架的指数仍不能低于 1.9533。
   因此全布局最优值位于 [1.9533,1.9586106)，精确极限尚未找到。

这里“下限”指当前成本上界公式和盒子约束所能认证的指数下限；
不是算法真实耗时下界，更不是 3SUM 问题的下界。
下界假设 beta<0、固定盒子预算、按前缀报告、缺失比例<=1/2。

完整推导：LIMIT_PROOF.txt。
上界证书：profile_certificate.json / verify_profile.py。
固定布局下界：fixed_profile_barrier.json / verify_fixed_barrier.py。
全布局下界：all_profile_barrier.json / verify_barrier.py。
运行输出分别保存在 *_verification.json；浮点探索文件没有证明效力。

从项目根目录复验（只需 Python 标准库）：
  python "3 SUM/research/heterogeneous_limits_2026-10-14/verify_profile.py" --self-test
  python "3 SUM/research/heterogeneous_limits_2026-10-14/verify_fixed_barrier.py"
  python "3 SUM/research/heterogeneous_limits_2026-10-14/verify_barrier.py"
  python "3 SUM/research/heterogeneous_limits_2026-10-14/check_three_type_core.py"

重新选择见证才需要 SciPy/NumPy：build_profile.py、build_fixed_barrier.py、
build_barrier.py。验证器使用上一轮 v3 的 Fraction 对数区间库。
build_profile.py 从 integer_profile.json 的浮点搜索记录生成有理布局；
下界生成器只选择矩形和熵见证，其验证器重新检验每条不等式及完整覆盖。

继承的数学核心与尚未完成的桥接见：
  ../algorithm_search_2026-10-14/ALGORITHM_AND_PROOF.txt
  ../algorithm_search_2026-10-14/MIXED_RADIX_PROOF.txt
本轮新增三种块尺寸 (6,8,10)，340200 个精确查询全部通过；
有限原型检验结果：three_type_core_results.json。

数值搜索记录：profile_search.json、extended_search.json、integer_profile.json。
优化器 success 不是证明；未收敛候选和经分裂的种子都有记录。
extended_search.json 中被后续种子分裂影响的历史项已重新计算成本并标注。

最有价值的下一步：改变布局的全局形状、尝试随深度变化的盒子预算，
以及关闭 H2/H3。固定当前九段布局后，单纯继续调标量参数的空间已很小。
