# 固定来源、接口与审计范围

检索/分析日期：2026-10-14。
源仓库：c0ldzy17/three-sum-lean。
固定提交：`2b639655e07421b9ac743de9090459bab473a7c0`。

本次 Big O Speedrun 的网页仍把 1.962 列为 Lean Verified 首项。
本包不是平台提交，也不作全球新颖性/科学优先权认定。

## 本轮直接读取的主来源

1. 算法组成和继承关系，完整 METHOD.md：
   https://github.com/c0ldzy17/three-sum-lean/blob/2b639655e07421b9ac743de9090459bab473a7c0/METHOD.md
   Git blob SHA: `525081d8396b947f6c6bfbbc4d9b75cc8a93a03d`。
2. 解析定义、开关、统一熵界、十二项成本表：
   https://github.com/c0ldzy17/three-sum-lean/blob/2b639655e07421b9ac743de9090459bab473a7c0/Submission/ThreeSum/Parameters.lean
   读取行段：1–230、330–580（后一个工具响应末端被截断，不能声称读完文件）。
   Git blob SHA: `8f62d54770b6a5215e6a4ab81f4c3260d583881e`。
3. 原可执行分块尺寸、固定局部扩张和原1/5比例：
   https://github.com/c0ldzy17/three-sum-lean/blob/2b639655e07421b9ac743de9090459bab473a7c0/Submission/ThreeSum/Scales.lean
   读取行段：1–160。
   Git blob SHA: `55c1f8ff8943d2fe1c3ddf6f55592412529534b6`。
4. 一般L,h的局部覆盖数目、均值与素数参数，以及固定512h的实例：
   https://github.com/c0ldzy17/three-sum-lean/blob/2b639655e07421b9ac743de9090459bab473a7c0/Submission/ThreeSum/LocalCoverBounds.lean
   读取行段：1–220、220–420（包含文件结尾）。
   Git blob SHA: `b4575c82a13ee2e5e9709760af8bc73d1a2a55ea`。
5. 当前纪录标签与统一模型：
   https://bigospeedrun.com/3sum

这些文件通过GitHub连接器读取。本轮并未下载、编译或逐行审查整个上游依赖
闭包；一次公开源码ZIP下载因网络解析失败，没有被当作成功获取。

## 从上一轮承接的材料

- `3sum_1962_push_2026-10-14/RESEARCH_NOTE.md`
- `3sum_1962_push_2026-10-14/verify_refinement.py`
- `3sum_1962_push_2026-10-14/rational_interval.py`

本轮重新检查了关键源定义，重做了每份证书的全部数值，而不是引用上一轮
浮点结果作为已证明前提。exact_interval.py沿用上一轮开发的标准库有理
区间实现，并去掉不使用的浮点数学导入。

## c=232 的变化不只是改证书

- 局部宇宙从256s改成232s，即512h改成464h；
- outputCount/vertexCount/degree、selectedPrime阈值必须用一致的新L；
- E、kappa、gamma由同一新c计算；
- 整数分块比例、分带除数和开关必须同步；
- 上层稀疏查询、表建立、报告和字长/寻址成本需要重新组合检查。

LocalCoverBounds中的一般L,h恒等式和有限界解释了局部参数变化的数学基础。
它们不是整个上游运行时间定理已支持任意c的证据。本包对此保留清楚的
条件边界。PROOF.md给出本轮完成的连续/有限数学推导。

## 归属

上游METHOD.md明确致谢Alman与Vassilevska Williams、Björklund/Husfeldt/
Kaski/Koivisto、Swapnil Jain、Anthropic及其经Jihoon Hyun工程继承的形式化
基础。本包不把这些算法、归约、子集卷积或机器模型重新归为自己的贡献。
本轮新增的是正系数多项式证书、参数见证和固定模型下界证明；其全球新颖性
未经穷尽检索确认。
