这份材料是本地投稿准备包，尚未发布到 Hexagon。

hexagon_source.zip：供 Hexagon 上传的论文源文件包，内含 main.tex。
main.tex：单文件英文论文，内嵌参考文献，无外部图片或 .bib 依赖。
main.pdf：本地编译后的阅读版（生成成功后提供）。
FORM_CONTENT.txt：可复制的标题、摘要、分类、署名和 AI 来源声明。
verification_bundle.zip：独立的本地复现包，不是 Hexagon 论文上传包。
MANIFEST.sha256：最终文件的 SHA-256 校验值。
build/：本地编译日志和排版检查产物，不应上传。

提交步骤
1. 用本人 ORCID 登录 Hexagon。
2. 按 FORM_CONTENT.txt 填写，姓名以账号实际情况为准。
3. 上传 hexagon_source.zip，主入口为 main.tex。
4. 检查网站生成的预览。
5. 自行选择许可并据实确认表单声明，再决定是否提交。

明确的状态
- 正文提出的是依赖已引用算法及归约的纸面运行时间证明。
- 本次改进没有完整 Lean 形式化；原上游形式化也未在此次完整重建。
- 提交者已说明尚未逐步核查，因此 human understanding 记录为 none。
- 当前来源声明准确描述本次整理与检查；未补造最初研究笔记的模型或生成历史。
- 主标题含 O(n^1.999017)，另一组 O(n^1.999073) 参数在正文单独说明。
- 许可尚未选择，材料准备不代表已经同意网站的发布声明。

本地复现
解压 verification_bundle.zip 后，在该目录运行：
python reproduce.py
核心检验只依赖 Python 标准库；可选 --optimize 需要 SciPy。

编译
main.tex 使用常见 LaTeX 宏包，可用 Tectonic 编译，或用 pdfLaTeX 编译两次。
已安装编译器时可执行：
tectonic main.tex
或：
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
