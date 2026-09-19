# ⚠️ 使用限制与学术诚信声明

> [!WARNING]
> 本项目只做**实验报告的格式与排版自动化**：把实验目的、仪器、原理、操作步骤
> 排进模板，把本人实测的原始数据填进记录表，画原理图，导出 PDF。
>
> **它不生成实验内容，不生成实验数据，也不替你做实验。**
>
> - 实验原理、操作步骤必须来自课程材料，不得让模型凭空编造；
> - 原始数据必须来自本人实测，**严禁编造、补齐、"估算"任何测量值**；
> - 原始数据记录表仍需指导老师签字确认；
> - 使用者对提交内容的真实性负全部责任。
>
> 本项目的设计也刻意配合这一点：数据由使用者提供、脚本只做自洽性校核并在
> 发现异常时**提示**而非"修正"，签字栏始终保持空白。
>
> **严正反对任何学术不端行为。** 请遵守你所在学校的学术规范；
> 若学校不允许使用此类工具，请不要使用。
>
> 本项目按"现状"提供。在适用法律允许的最大范围内，作者和贡献者不对其准确性、
> 完整性、特定用途适用性或使用结果作出明示或默示保证。具体责任限制以
> [LICENSE](./LICENSE) 及适用法律为准。

# Physics Lab Report Skill

一个用于生成、更新并导出**大学物理实验报告**的 Agent Skill。
交给它实验名称，它写预习报告并画原理图；交给它原始数据，它填进记录表；
两种模式最后都导出为可直接提交的 PDF。

## 功能

- **预习模式**：填写封面与信息行 → 编写实验目的/仪器/原理/操作步骤 → 绘制原理图 → 导出 PDF
- **数据模式**：填入实验日期与原始数据记录表（支持真下标、框线、自动分页）→ 重新导出
- **原理图**：内置 `figstyle.py`，用 matplotlib 画结构图、光路图、受力图等，**自己生成而非下载网图**
- **信息管理**：姓名/学号/班级/老师等统一存在 `.profile`，缺失时主动询问，不在报告里硬编码
- **交付自检**：检查红字残留、插图数、正文格式、必填字段，并给出提交文件名
- **环境自检**：`lab.py doctor` 检查依赖、模板、个人信息与 LibreOffice，缺什么都能报出来

## 重要：模板需要自备

**本仓库不附带任何学校的实验报告模板文件**——模板是各学院自己印发的文档，
版权归原单位。

请自备一份空白模板，放到 `~/物理实验报告/templates/实验报告模板-空白.docx`：

1. 拿到你学校的模板；
2. 删掉里面的示例与批注文字（很多模板用红色文字写排版要求，那些是提示不是内容）；
3. 放到上述路径，或用环境变量 `PHYSLAB_TEMPLATE` 指向它。

本 Skill 的锚点设计见 [`reference/format.md`](./reference/format.md)；
模板结构不同也能适配，改锚点即可。

## 安装

### 使用 Skills CLI 一键安装（推荐）

需要已安装 Node.js 和 npm。`--agent` 的取值见
[skills 支持的 agent 列表](https://github.com/vercel-labs/skills#supported-agents)
（注意是 `claude-code`，不是 `claude`）：

```bash
# Claude Code
npx skills add AndyYang12345/physics-lab-report-skill --agent claude-code --global

# Codex
npx skills add AndyYang12345/physics-lab-report-skill --agent codex --global

# Cursor
npx skills add AndyYang12345/physics-lab-report-skill --agent cursor --global
```

跳过交互确认：

```bash
npx skills add AndyYang12345/physics-lab-report-skill --agent claude-code --global --yes
```

只查看仓库中可安装的 Skill，不执行安装：

```bash
npx skills add AndyYang12345/physics-lab-report-skill --list
```

`skills` 是第三方开源安装器。执行 `npx` 会下载并运行安装器代码；
安装前请确认仓库来源，需要可复现安装时请固定经过审核的 CLI 版本。

### 使用 Git 手动安装

```bash
git clone https://github.com/AndyYang12345/physics-lab-report-skill.git \
  ~/.agents/skills/physics-lab-report
```

安装后重新启动 Agent 或开启新会话，使其重新发现 Skill。

## 依赖

```bash
pip install python-docx Pillow matplotlib lxml
```

导出 PDF 还需要 **LibreOffice**（提供 `soffice` 命令）：

```bash
sudo apt install libreoffice-writer   # Debian / Ubuntu
brew install --cask libreoffice       # macOS
```

画中文原理图需要系统里有 CJK 字体，Linux 上装 `fonts-noto-cjk` 即可。

装好后先自检：

```bash
python scripts/lab.py doctor
```

## 使用

可以显式调用，也可以直接描述任务让 Agent 自动匹配：

```text
写一下"分光计的调整与使用"这次实验的预习报告。
```

```text
这是这次实验的原始数据（附截图），帮我填进报告并导出 PDF。
```

命令行等价于：

```bash
python scripts/lab.py profile                        # 看个人信息缺什么
python scripts/lab.py build  .build/<名称>/spec.json  # 预习模式：生成报告
python scripts/lab.py data   .build/<名称>/data.json  # 数据模式：填日期与原始数据
python scripts/lab.py export "<实验名称>"             # 导出 PDF 到 提交/
python scripts/lab.py check  "<实验名称>" --figs 3    # 交付前自检
```

工作目录结构：

```
~/物理实验报告/
├── .profile                        个人信息（唯一来源）
├── templates/实验报告模板-空白.docx   自备的空白模板
├── .build/<名称>/                   所有中间产物（docx / 图 / 脚本 / json）
└── 提交/<座位号>-<姓名>-<名称>.pdf    最终交付，只放 PDF
```

### 环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `PHYSLAB_HOME` | `~/物理实验报告` | 工作根目录 |
| `PHYSLAB_TEMPLATE` | `$PHYSLAB_HOME/templates/实验报告模板-空白.docx` | 空白模板路径 |

## 设计要点

这个项目里有几处踩坑换来的设计，对做类似工具的人可能有用：

- **锚点只用模板自带的固定标签**（`实验日期：`、`实验目的：`……），
  绝不用正文内容——正文是每次生成的，换个实验就失效；
- **不手搓 OOXML**，用 python-docx 封装。中文字体必须同时设 `w:eastAsia`，
  下标必须用 `vertAlign`（Unicode 下标字符 `₁₂₀` 在宋体里缺字形，
  Word 里会变方框），`rPr` 子元素顺序还受 schema 约束；
- **原理图自己画**：网图版权不明、分辨率不可控、符号常和正文公式对不上。
  自画才能保证图里的几何量与公式严格自洽（例如先由折射定律反解出
  `r = 30°`、`i = 53.13°`、`δmin = 46.26°`，再代进去画线）；
- **排版正确性只能靠看**：LibreOffice 不认表格单元格里的"与下段同页"，
  导出后必须目视核对分页；
- **验收标准是从零跑通**：删掉中间产物重新生成一遍，才能发现静态检查抓不到的 bug。

详见 [`SKILL.md`](./SKILL.md) 的「已知坑」一节。

## 适用性说明

本项目默认的模板结构、格式要求（宋体/小四/1.5 倍行距）与命名规范，
来自**华南理工大学物理与光电学院**的实验报告模板。其他学校需要按
[`reference/format.md`](./reference/format.md) 适配自己的模板与格式常量。

但 `scripts/labkit.py` 里的 docx 操作层（格式封装、锚点定位、表格、
分页、导出、自检）与 `reference/figures.md` 的方法论是通用的，
可以搬到任何"用 Agent 生成 Word 文档"的场景。

## 许可

本项目采用 [MIT License](./LICENSE)。
