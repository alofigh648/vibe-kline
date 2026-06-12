# vibe-kline

> 将 Claude Code 的编辑行为实时渲染为 K 线图。  
> 每一次文件改动都是一根蜡烛，像看盘一样回顾你的编程过程。

[English](README.md)

---

## 它做了什么

`vibe-kline` 通过 hook 接入 [Claude Code](https://claude.ai/code)，将每次文件编辑记录为一根 K 线蜡烛：

- **开盘 / 收盘** — 编辑前后的项目总行数
- **涨跌** — 增加行（绿）/ 删除行（红）
- **Session 色带** — 每个对话 session 对应一种颜色区域
- **Commit 标记** — git commit 处显示金色 ◆，悬浮查看信息和 hash
- **活跃热力图** — 侧边栏显示近 14 天的每小时编辑强度

图表自动轮询新数据，开着放在浏览器标签页里，边写边看。

## 环境要求

- Python 3.9+
- [Claude Code](https://claude.ai/code)
- Git（推荐；没有时回退到当前目录）

## 安装

把 vibe-kline 克隆到**机器上任意位置**，不需要放进项目目录：

```bash
git clone https://github.com/alofigh648/vibe-kline.git ~/tools/vibe-kline
cd ~/tools/vibe-kline
./install.sh
```

安装时选择两种模式之一：

### 全局模式 — 适用所有项目（推荐）

```bash
./install.sh --global
```

Hook 安装到 `~/.claude/hooks/`，对所有 Claude Code 会话生效。`kline.html` 会在首次编辑时自动复制到当前项目，或者立即复制：

```bash
./install.sh --init /path/to/my-project
```

### 项目模式 — 仅追踪单个项目

```bash
./install.sh --project /path/to/my-project
```

Hook 和 `kline.html` 安装到指定项目目录。不传路径则默认当前目录：

```bash
cd /path/to/my-project
./install.sh --project
```

## 使用

**1. 启动本地服务器**（在项目目录下运行，每次会话启动一次）：

```bash
cd /path/to/my-project
python -m http.server 38080
```

**2. 打开图表：**

```
http://localhost:38080/kline.html
```

用 Claude Code 开始编码，蜡烛实时出现。

## 图表功能

| 功能 | 说明 |
|---|---|
| K 线蜡烛 | 颜色 = 文件类型 · 亮度 = 变化幅度 |
| MA 均线 | 自适应移动平均线 · 点击图例切换显示 |
| 布林带 | 点击 **BB带** 按钮开关 |
| Session 色带 | 每个 Claude Code 对话对应独立色带 |
| Commit 标记 | ◆ 标在 git commit 处 · 悬浮查看 hash 和信息 |
| 时间断层 | 超过 30 分钟空窗期显示琥珀色徽章 |
| 活跃热力图 | 侧边栏 14 天格子（小时 × 日期） |
| 回放 | ▶ 按钮重演整个 session |
| 文件聚焦 | 点击排行榜中的文件名，高亮该文件的蜡烛 |
| 导出 PNG | 一键保存当前视图 |

## 键盘快捷键

| 按键 | 功能 |
|---|---|
| `← →` | 逐蜡烛导航 |
| `+` / `-` | 缩放 |
| `Space` | 跳到最新 |
| `Home` | 跳到第一根 |
| `Esc` | 取消文件聚焦 |

## 数据文件

| 文件 | 说明 |
|---|---|
| `.claude/kline_data.json` | 完整内部数据（私有） |
| `kline_data.json` | 图表轮询用的公开导出 |
| `kline.html` | 独立的图表查看器 |

建议在 `.gitignore` 中添加：

```
kline.html
kline_data.json
.claude/kline_data.json
```

也可以把 `kline.html` 提交进仓库，与团队分享当前 session 快照。

## 工作原理

```
Claude Code 编辑文件
    │
    ├── PreToolUse hook  → 记录编辑前行数（蜡烛开盘）
    │
    └── PostToolUse hook → 记录编辑后行数（收盘）→ 写入蜡烛 → 更新 kline.html
                                ↑
                       kline_utils.py 通过 git 或 cwd 确定项目根目录
```

数据直接通过标记注释嵌入 `kline.html`，无需数据库，无需构建步骤。

## 卸载

**全局模式：**
```bash
rm ~/.claude/hooks/pre_tool_use.py \
   ~/.claude/hooks/post_tool_use.py \
   ~/.claude/hooks/kline_utils.py
```

**项目模式：**
```bash
rm .claude/hooks/pre_tool_use.py \
   .claude/hooks/post_tool_use.py \
   .claude/hooks/kline_utils.py
```

## 许可证

MIT
