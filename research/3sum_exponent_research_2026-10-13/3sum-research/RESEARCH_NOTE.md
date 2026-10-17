# 3SUM Exponent：检索、参数改进与尾和精化

日期：2026-10-13。

**状态声明：**本文包含外部已公开结果、对既有定理的参数推论，以及一个新的纸面计数精化。算术不等式已经用精确有理数区间运算复核。没有运行完整 Lean 工程，没有提交 Prove2Me，不应把本文候选结果列为已经形式化认证的纪录。所谓“新”指本次独立推导；没有证明全球优先权。

## 1. 可核实的基线

Prove2Me 的 3SUM Exponent campaign 在检索时列出四个完成的目标：1.9992、1.99913、1.999112、1.999074。最后一项于 2026-10-07 获 ACCEPTED，目标状态为 PROVED。它要求多项式有界整数输入、确定性 word-RAM 程序、最坏情况时间；输入中必须存在三个两两不同下标，其值之和为零。重复值允许，重复下标不允许。[1][2]

原始论文为 Josh Alman 与 Virginia Vassilevska Williams 的 *Truly Subquadratic 3SUM and Truly Subcubic APSP via Triangles in Sparse Lopsided Graphs*，arXiv:2610.06783v1，2026-10-05 提交。其确定性整数输入界为 O(n^1.9992)，另有 real-RAM 上 Las Vegas 期望时间 O(n^1.998)。后者不能直接充当上述确定性 word-RAM 目标的证明。[3]

检索还找到预处理宇宙下 O(n^1.5 log n) 的查询界，但需先付二次预处理成本，不是一次性一般 3SUM 的对应纪录。[7] 本次公开网页、论文与代码检索未核实到比 1.999074 更小的、符合 campaign 同一模型且已认证的公开界。这不是穷尽全网或优先权证明。

## 2. 将已有框架写成可优化公式

以下符号改写了原项目 Corollary 31、Theorem 30、Exact Triangle 归约的成本，不改变其计算模型。[3][4][5]

令 H(x)=-x ln x-(1-x)ln(1-x)，所有对数为自然对数。对 c>10、0<theta<0.9，定义

```
gamma(c,theta) = theta * ln((c-1)/9) / ln(4)
q(theta) = [H(theta) + theta*ln(9)] / ln(4)
A(c) = [c*ln(10) - c*H(1/c)/2 - (c-1)*ln(3)] / ln(4)
R(c,gamma) = 1/[A(c)+gamma].
```

选择 a<R(c,gamma)，内维 D 大致为 N^a。已证明的内层算法在预处理后支持指定位置查询。若指定位置数不超过 N²/sqrt(D)，则总成本可写为

```
O-tilde(N² * [D^(-gamma) + D^(q-1/2)]).
```

因此，一个可用的内层节省指数 s 必须满足

```
0 < s < min(gamma, 1/2-q).
```

这里 O-tilde 隐去对数因子，但不允许悄悄隐去一个固定正数的指数。

### 完整归约的成本

Exact Triangle 的规模记为 n。选择 D=4^m 为不超过 n^a 的最大 4 的幂，g=ceil(D^b)。小规模单独穷举。D 位于 (n^a/4,n^a]，所以取整只改变常数，不改变幂指数。所有参数都是固定有理数；D、g 可通过整数幂比较计算，不需要机器具有实数幂或对数指令。

按既有归约逐项计算：

| 项目 | n 的指数（忽略对数因子） |
|---|---:|
| 内层问题总成本 | 3+a(b-s) |
| 扫描 | 3-ab |
| 选择素数 | log_2(7)+(3/2)a |
| 构建实例 | 2+a(1+b) |

对前两项取 b=s/2。还必须验证后两项严格小于 3-as/2。由已知确定性归约，3SUM 成本为

```
n^(2-as/4+o(1)).
```

所以任何严格大于 2-as/4 的固定目标指数，都可以吸收这些 o(1) 与对数因子；边界值本身不能这样声称。这也是验证脚本专门检查正裕量的原因。[3][6]

## 3. 改进 A：仅重调现有参数

已完成的 1.999074 mission 使用 c=22、theta=0.11229、D 约为 n^0.054、g 约为 D^0.0343。[2]

保留 c、theta，改为

```
c=22
theta=0.11229
a=0.05405
s=0.06862
b=0.03431=s/2.
```

精确有理区间校验得到（下列小数只是显示值；判定使用有理数端点）：

```
gamma in [0.068631222495934868, 0.068631222495934869]
q     in [0.431367880323245422, 0.431367880323245423]
R     in [0.054052515527303591, 0.054052515527303592].
```

因此 gamma>s、1/2-q>s、a<R 都严格成立。Exact Triangle 主项指数为 2.9981455445，3SUM 的边界指数为

```
2-a*s/4 = 1.99907277225 < 1.999073.
```

目标差为 0.00000022775，是严格正数。选择素数与构建实例的指数也严格小于 Exact Triangle 主项。故按已有框架的纸面代入，可以得到 **O(n^1.999073)**，无需改变内层算法的计数原理。

**认证边界：**这不是对既有顶层 1.999074 定理使用单调性就能推出的结论；必须实例化更一般的内层定理，并重做 Exact Triangle 到 3SUM 的总成本连接。本文没有提供或运行这条连接的完整 Lean 证明。

对原公式做的连续数值搜索在 c≈22.218280、theta≈0.112063613 附近得到边界约 1.999072507710。这个数只是探索结果，不是全局最优性证书，也不是可以直接宣称的 Big-O 端点。

## 4. 改进 B：保留精确二项式尾和

这一节是本次独立推导，不是外部榜单结果。

### 4.1 需要精化的位置

原项目中，阶数 d 的叶子数及归一化规模为

```
beta_d = binom(L,m-d) * 9^(L-m+d)
M = beta_0.
```

Theorem 30 的证明在应用统一几何衰减界之前，每个 tile 的 box 处理成本是

```
O(L*(m+1)*sum_{d=t}^m beta_d).
```

tile 数为 O(N²/M)。源码将精确尾和进一步上界成 M*rho^t/(1-rho)，其中 rho=9m/(L-m+1)。这个替换方便，但在 t 为 m 的固定比例时会损失一个固定指数。[5]

重要：不能把新的 gamma 直接塞进已证明的 Corollary 31，因为那个定理绑定的是旧 gamma。必须回到上述尚未放松的成本式，并证明一个新运行时间推论。

### 4.2 可复用尾和引理（先取整数 c，已足够实现候选）

固定整数 c>10，L=cm，D=4^m，t=ceil(theta*m)，0<theta<0.9。定义

```
gamma_star(c,theta)
 = [c*H(1/c)-c*H((1-theta)/c)-theta*ln(9)]/ln(4).
```

则存在仅依赖 c、theta 的常数 C，使

```
sum_{d=t}^m beta_d / M <= C*(m+1)*D^(-gamma_star).
```

下面给出含有限规模处理的证明。

**第一步：从 beta_t 而不是 beta_0 开始估计尾部。**

对 1<=d<=m 有精确比值

```
beta_d/beta_(d-1) = 9*(m-d+1)/(L-m+d) <= rho < rho_c=9/(c-1)<1.
```

从 t 开始累加几何级数，得到

```
sum_{d=t}^m beta_d <= beta_t/(1-rho_c).
```

当 t=m 时仍然成立；由于 theta<1 且 m>=1，t<=m。

**第二步：二项式熵界。**

对 0<=k<=r，令 p=k/r，并约定 H(0)=H(1)=0，有

```
exp(r*H(p))/(r+1) <= binom(r,k) <= exp(r*H(p)).
```

上界来自二项分布的对应单项概率不超过 1。下界来自在 p=k/r 时，该项是最大概率项，而 r+1 项的概率之和为 1。k=0 或 k=r 可直接检验。

应用到 beta_t/M，设 u=t/m，得到

```
beta_t/M
 <= (cm+1) * exp(m*{c*H((1-u)/c)-c*H(1/c)+u*ln(9)}).
```

函数 F(u)=c*H((1-u)/c)+u*ln(9) 在 0<=u<1 上满足

```
F'(u)=ln(9*(1-u)/(c-1+u))<0.
```

它在 u=1 连续延拓。因此 u>=theta 时 F(u)<=F(theta)，无需把 t=ceil(theta*m) 当成实数 theta*m。于是

```
beta_t/M <= (cm+1)*D^(-gamma_star).
```

结合第一步即可。特别是 c=21 时，有显式界

```
sum_{d=t}^m beta_d/M <= (20/11)*(21m+1)*D^(-gamma_star).
```

**第三步：新指数确实严格更好。**

两个 gamma 在 theta=0 时都为 0，而

```
(d/dtheta)gamma_star = ln((c-1+theta)/(9*(1-theta)))/ln(4)
(d/dtheta)gamma      = ln((c-1)/9)/ln(4).
```

theta>0 时前者严格较大，所以 gamma_star>gamma。此处只证明同一 c、theta 下的预处理指数改善；不能忽略查询指数 q 和编码成本，直接把它称作最终 3SUM 改善。

### 4.3 从计数接回算法

将新尾和界放回未放松的 box 成本，得到

```
boxes = O(N²*(log D)^3/D^gamma_star).
```

额外的一个 log D 来自使用简单熵界产生的 m+1 因子，不应漏掉。不过它不改变以下固定幂指数。

查询枚举没有改变，仍为 O(D^q log D) 每项。编码成本满足

```
encodings = O(N*D^A*sqrt(log D)).
```

如果 a*(A+gamma_star)<1，且 D<=N^a，那么编码成本为 O(N²/D^gamma_star)，因为剩余的固定幂裕量足以吸收 sqrt(log D)。tile-fit 条件也成立：记 B=log_4(sqrt(M))/m 的渐近指数，由 M<=10^L 得 A>=B，故编码条件比所需 N>=sqrt(M) 强。

因此，给定 |W|<=N²/sqrt(D)，对任意

```
0<s<min(gamma_star,1/2-q)
```

可得到 O(N²/D^s) 的内层总时间，或在边界记作 O-tilde(N²/D^min(...))。算法只改变参数及分析，不新增随机性；所有编码与索引仍为多项式大小整数，保持原 word-RAM 模型。不过 Lean 工程仍需把未放松的 box 数量接回程序运行步数，不能仅证明一个实数不等式就结束。

### 4.4 便于形式化的有理参数

取

```
c=21
theta=0.11202
a=0.05665
s=0.06945
b=0.034725=s/2.
```

严格区间：

```
gamma_star in [0.069454625736072798, 0.069454625736072799]
q          in [0.430536990526086701, 0.430536990526086702]
R_star     in [0.056657067725264770, 0.056657067725264771].
```

所有必要不等式严格满足。重新代入完整归约得到

```
Exact Triangle: O-tilde(n^2.99803282875)
3SUM: n^(1.999016414375+o(1))
     <= O(n^1.999017).
```

这里 1.999017 比边界大 0.000000585625。选择素数的指数约为 2.89232992206；构建实例指数为 2.05861717125，均明显低于 Exact Triangle 主项，没有遗漏一个更慢阶段。

**结论层级：**这是一份带有具体计数证明、完整成本代入和精确算术验证的算法分析候选。它需要独立数学审计和机器模型成本的完整 Lean 接线，才能称为已认证改进。本文不声称发现了新的矩阵乘法张量或新的归约。

对新公式的探索性连续优化给出边界约 1.999016131404，参数 c≈20.788557、theta≈0.112251498。它不是全局最优性证明。本文的实际候选刻意取整数 c=21，以简化 L=cm 的取整证明。

## 5. 最小形式化路线

优先复用原工程的定义、引理和归约，不重建 word-RAM。

1. 提取或复用参数化转移定理：内层时间界 + 四项成本条件 -> Exact Triangle 指数 -> 3SUM 指数；先认证 1.999073。
2. 证明有限尾和 <= beta_t/(1-rho_c) 与上面的熵尾和引理。先只实现 c=21 或整数 c，避免把实数 c 的 ceil 处理放入第一轮。
3. 在 Theorem30.boxes_total / boxes_cost 之前保留精确尾和，修改或补充其程序耗时界；构建 sharp 版 Corollary31/32。
4. 实例化有理参数、处理小 n 和参数的整数计算、吸收对数及 n^o(1)，最后检查顶层结论仍是原 EndStatement.ThreeSum.SolvedInTime。

必须检查：新引理无 sorry、无新增未经证明的运行时间公理、输入的不同下标语义不变、最终程序为确定性、固定字长常数可依赖输入大小上界指数但不能依赖实际输入、全部程序成本被覆盖。网页上的目标占位符不能用于判断其实际证明是否含 sorry；应检查具体 Solution 与依赖。

## 6. 复现和验证范围

运行：

```sh
python verify_exponents.py
# 可选；需安装 scipy，仅用于探索性浮点寻优：
python verify_exponents.py --optimize
```

验证器的对数使用

```
ln(x)=2*sum_{k>=0} z^(2k+1)/(2k+1), z=(x-1)/(x+1).
```

先把 x 通过 2 的幂约化到 [1,2]，因此 0<=z<=1/3。截断 K=48 项后的余项被显式有理上界

```
2*z^(2K+1)/((2K+1)*(1-z²))
```

包住。所有区间运算与不等式判定均使用 Python Fraction；打印的十进制端点向外舍入。浮点只用于可选数值寻优。脚本另外对 c=21、m=1,...,100 的有限尾和执行了整数不等式检查，但该有限测试不替代渐近证明。

验证输出保存在 verification_output.txt。没有下载编译整个 Lean 工程，没有提交任何外部平台。若要发表，应先完成数学/形式化审计和再次检索。

## 来源

[1] Prove2Me, 3SUM Exponent campaign，检索于 2026-10-13。
<https://prove2.me/campaigns/3sum-exponent>

[2] Prove2Me, 3SUM in O(n^1.999074) Time on a Word RAM，Goal PROVED / ACCEPTED 2026-10-07。
<https://prove2.me/missions/3SUM_in_O%28n%5E1.999074%29_Time_on_a_Word_RAM>

[3] Alman & Vassilevska Williams, arXiv:2610.06783v1。本文依赖其第 3 节的归约与第 4 节的逐项算法成本。
<https://arxiv.org/abs/2610.06783>

[4] 原始形式化代码，Corollary31.lean；复现建议固定原始提交 e1a4e6508154ea59f030480661590a9fe3018011，而非无版本 main。
<https://github.com/anthropics/formal-math/blob/e1a4e6508154ea59f030480661590a9fe3018011/3sum-apsp/ThreeSumApsp/Sec4/Corollary31.lean>

[5] 原始形式化代码，Theorem30.lean、Lemma29.lean；读取的计数定义和几何界。
<https://github.com/anthropics/formal-math/blob/e1a4e6508154ea59f030480661590a9fe3018011/3sum-apsp/ThreeSumApsp/Sec4/Theorem30.lean>
<https://github.com/anthropics/formal-math/blob/e1a4e6508154ea59f030480661590a9fe3018011/3sum-apsp/ThreeSumApsp/Sec4/Lemma29.lean>

[6] 原始形式化项目 README，说明机器模型、各结论的认证范围和复核方式。
<https://github.com/anthropics/formal-math/tree/e1a4e6508154ea59f030480661590a9fe3018011/3sum-apsp>

[7] Kasliwal, Polak & Sharma, 3SUM in Preprocessed Universes: Faster and Simpler, arXiv:2410.16784。
<https://arxiv.org/abs/2410.16784>
