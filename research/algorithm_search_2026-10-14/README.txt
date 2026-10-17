3SUM 新方向实验：异质微块候选
2026-10-14

本轮结果：找到并验证一个新查询/编码核心。
前34.0200365%的微块用扩张72，后段用扩张252；条件目标指数1.95923。
这突破了“所有块同一个c”的模型限制；不是对旧模型再调小数。

已经完成：
  * 核心算法的一般有限正确性证明及9450组精确带权查询核对；
  * 131个有理仿射调度区间覆盖全部连续层数；
  * 全部十二项条件成本 <1.959226<1.95923；
  * 四项伪造证书拒绝测试；
  * 异质混合基数的有限覆盖/表示数/输出键证明，6147组目标对核对。

尚未完成：
  * H2：接回原始输入过滤、wanted/false质量保护；
  * H3：完整word-RAM实现及耗时、字长、地址的组合证明。
因此不能把1.95923称为已证明的完整3SUM算法复杂度或平台纪录。

阅读顺序：
  DIRECTIONS.txt                 三条结构方向的尝试及筛选
  ALGORITHM_AND_PROOF.txt         新核心、连续证明和确切开放条件
  MIXED_RADIX_PROOF.txt           混合基数连接证明
  heterogeneous_verification.json 精确成本及区间结果

复验（从项目根目录运行，Python标准库即可）：
  python "3 SUM/research/algorithm_search_2026-10-14/finite_core.py"
  python "3 SUM/research/algorithm_search_2026-10-14/mixed_radix.py"
  python "3 SUM/research/algorithm_search_2026-10-14/verify_heterogeneous.py" --self-test

只有探索和重新生成见证需要SciPy，探索不参与精确验收：
  explore_heterogeneous.py、build_heterogeneous_certificate.py
验证器依赖同级目录保留的v3有理区间库；本目录不单独打包为独立程序。

没有修改旧v3或上一轮排除证书。没有外部提交、发布或完整Lean构建。
