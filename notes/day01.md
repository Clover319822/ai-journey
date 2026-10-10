# Day 1 · 2026-10-10 · 环境打通

今天没写代码，但把地基打完了。目标是明天开始能直接进 Python 和 API。

## 完成的事

- [x] GitHub 账号注册完成（用户名 `Clover319822`，2026-10-10 建号）
- [x] 生成 ed25519 SSH 密钥并绑定到 GitHub
- [x] `ssh -T git@github.com` 验证通过
- [x] 配置 git 全局身份与基础参数
- [x] 本仓库初始化 + 第一个 commit

## 环境参数

```
git        2.55.0.windows.3
user.name  Clover319822
init.defaultBranch = main
core.autocrlf      = input   # 避免 Windows / Linux 换行符冲突
```

## 踩过的坑：GitHub 网页打不开

**现象**：注册账号时页面长期白屏 / 转圈。

**排查过程**：
1. `nslookup github.com` —— DNS 正常，各家 DNS 都解析到 `20.205.243.166`，不是解析问题
2. 查 Windows 系统代理 —— `ProxyEnable=0`，没开代理，也没有第三方代理软件
3. 绕过本地代理直连测试 —— 3 次里 1 次超时、2 次成功

**结论**：国内直连 GitHub 是**间歇性超时**，不是被封死。同一 IP 反复重试即可。

**无效方案（别浪费时间）**：
- 改 hosts：实测 7 个 GitHub IP，当前 DNS 给的 `20.205.243.166` 已经是最快的（3/3 成功，0.24s），改了没收益
- 镜像站：`ghfast.top` 403、`ghproxy.net` 403、`gh-proxy.com` 404、`hub.gitmirror.com` / `gh.llkk.cc` 无响应。这些只代理 git clone 和 raw 文件，**代理不了网页登录**
- 加速工具官网 `steampp.net` 当时也不可达

**有效方案**：反复刷新；换手机热点；后续可装 Watt Toolkit（原 Steam++）或 FastGithub 做长期加速。

## 学到的

- SSH 有两个端口可用：22（`git@github.com`）和 443（`git@ssh.github.com`）。
  我这边的 22 端口没被封，所以不用配 ssh over 443 那套。
- 公钥和私钥的区别：`.pub` 结尾的公钥交给 GitHub，不带 `.pub` 的私钥永远不能给别人。
- WorkBuddy 的内置预览面板是独立浏览器环境，**不共享 Chrome/Edge 的登录 cookie**，
  涉及登录态的站点得用自己的浏览器打开。

## 明天

- Python 环境（用 uv 装，比 pip 快）
- CS50P 第 0 课
- 注册 Anthropic / DeepSeek API，跑通第一个 hello world 调用
