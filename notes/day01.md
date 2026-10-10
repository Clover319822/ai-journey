# Day 1 · 2026-10-10 · 环境打通

今天没写业务代码，但把地基打完了。目标是明天开始能直接进 Python 和 API。

## 完成的事

- [x] GitHub 账号注册完成（用户名 `Clover319822`，2026-10-10 建号）
- [x] 生成 ed25519 SSH 密钥并绑定到 GitHub
- [x] `ssh -T git@github.com` 验证通过
- [x] 配置 git 全局身份与基础参数
- [x] 本仓库初始化 + 推送到远端
- [x] 装好 uv 与项目虚拟环境，装好 anthropic / openai SDK
- [x] 写了 `week01/hello_llm.py`，冒烟测试通过

## 环境参数

```
git        2.55.0.windows.3
python     E:\Python\python.exe（3.14.8）—— 注意 PATH 里第一个 python 不是它
uv         0.13.0
user.name  Clover319822
user.email Clover319822@users.noreply.github.com
init.defaultBranch = main
core.autocrlf      = input   # 避免 Windows / Linux 换行符冲突
```

## 踩坑一：GitHub 网页打不开

**现象**：注册账号时页面长期白屏 / 转圈。

**排查过程**：
1. `nslookup github.com` —— DNS 正常，各家 DNS 都解析到 `20.205.243.166`，不是解析问题
2. 查 Windows 系统代理 —— `ProxyEnable=0`，没开代理，也没有第三方代理软件
3. 绕过本地代理直连测试 —— 3 次里 1 次超时、2 次成功

**结论**：国内直连 GitHub 是**间歇性超时**，不是被封死。反复重试即可。

**无效方案（别浪费时间）**：
- 改 hosts：实测 7 个 GitHub IP，DNS 给的 `20.205.243.166` 已经是最快的（3/3 成功，0.24s）
- 镜像站：`ghfast.top` 403、`ghproxy.net` 403、`gh-proxy.com` 404、`hub.gitmirror.com` / `gh.llkk.cc` 无响应。它们只代理 git clone 和 raw 文件，**代理不了网页登录**
- 加速工具官网 `steampp.net` 当时也不可达

**有效方案**：反复刷新；换手机热点；后续装 Watt Toolkit（原 Steam++）或 FastGithub。

## 踩坑二：git 配置被仓库级设置覆盖

改完全局 `user.email` 后，commit 作者仍是旧的 noreply 地址。

**原因**：git 配置分三级，**仓库级 `.git/config` 覆盖全局级**。建仓库时曾在仓库级设过一个 noreply。

**记住**：查"实际生效值"用不带 `--global` 的命令。

```bash
git config user.email          # 实际生效值
git config --global user.email # 全局值，可能被覆盖
```

## 踩坑三：开启邮箱隐私后 push 被拒

```
! [remote rejected] main -> main (push declined due to email privacy restrictions)
```

在 GitHub → Settings → Emails 勾上 **Keep my email addresses private** 后，
GitHub 会拒绝任何暴露真实邮箱的 push。解决办法是把本地 `user.email` 改成 noreply 地址。

**注意**：commit 归因看的是"邮箱是否属于该账号"，不是"是否等于登录邮箱"。
用 noreply 提交，绿格子照常记。

## 踩坑四：`git rebase --root --exec` 删掉了整个 .git

想把历史里两个 commit 的作者统一改成 noreply，用了：

```bash
git rebase --root --exec 'git commit --amend --reset-author --no-edit'
```

结果是 `.git` 目录直接没了，报错 `could not mark as interactive: No such file or directory`。
工作区文件完好，远端有完整备份，所以没造成损失。

**恢复方式**：备份文件 → `git init` → `git checkout --orphan main` → 分批 `git add` + `commit`
重建历史 → `git push --force`。

**结论**：这台机器（Git Bash / Windows）上**永远不要用 `git rebase --root --exec`**。
要批量改历史作者，用 `--orphan` 重建或 `git filter-repo`。

## 学到的

- SSH 有两个端口可用：22（`git@github.com`）和 443（`git@ssh.github.com`）。
  我这边 22 没被封，不用配 ssh over 443 那套。
- 公钥 `.pub` 交给 GitHub，不带 `.pub` 的私钥永远不能给别人。
- WorkBuddy 内置预览面板是独立浏览器环境，**不共享 Chrome/Edge 的登录 cookie**，
  涉及登录态的站点得用自己的浏览器打开。
- 公开仓库的 commit 作者邮箱是**任何人都能通过 API 读到的**。不想被爬虫拿走就用 noreply。
- PATH 里第一个 `python` 是 WorkBuddy 的运行时，不是我自己装的。装包要用
  `E:/Python/python.exe -m pip install`，否则装到别人家去了。

## 2026-10 可用的 Claude 模型（查证过）

| model id | 输入/输出（每百万 token） | 定位 |
|---|---|---|
| `claude-opus-5-5` | $4 / $20 | 复杂 agentic 任务 |
| `claude-sonnet-5-5` | $2 / $10 | 日常主力档，Sonnet 默认 |
| `claude-haiku-5-5` | $0.10 / $0.50 | 便宜 20 倍，跑量用 |

Sonnet 4.5 将于 2026-11-30 下线。

## 第一个真实调用（22:47 跑通）

```
供应商 : DeepSeek
模型   : deepseek-chat

原标题 : 新款简约现代抱枕套 客厅沙发靠垫套 45x45cm 不含芯
改写后 : Modern Throw Pillow Cover 45x45cm for Couch Sofa Living Room

输入 token: 147
输出 token: 17
```

**复盘这次输出哪里不够好**（明天优化 prompt 的方向）：

1. 没写材质。原标题也没给，但真实 listing 一定要有 —— 买家搜 "linen pillow cover" 不会搜 "modern"
2. 没写数量（1 片还是 2 片装），这是 TEMU 买家的核心关切
3. `Throw Pillow Cover` 是对的，这个词比 `Cushion Cover` 在北美搜索量高
4. 没提场景词 `Decorative`，也没提"不含芯"（Insert Not Included），后者能显著减少退货纠纷

**成本**：164 个 token，单次花费可以忽略。但记住这个数量级 ——
一次普通对话约几百 token，一个跑飞的 Agent 循环一晚上能烧掉几十万 token。
从第一个脚本开始就盯着 `usage` 这两个数字，这是后面做成本控制的地基。

**不需要装 DeepSeek 软件**：模型跑在对方服务器上，我们只是发一个 HTTPS 请求过去拿结果。
本机装的 `openai` / `anthropic` 这两个库只是"发请求的工具"，不是模型本身。

## 明天

- CS50P 第 0 课
- Python 基础：数据类型、控制流、函数
- 优化这个改写 prompt：补上材质、数量、是否含芯，并加一条"输出严格 JSON"
