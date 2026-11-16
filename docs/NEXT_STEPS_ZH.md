# 个人通讯录作业后续操作

按你的最新说明，本次个人完成、无需 Fork。截止时间为北京时间
2026 年 11 月 17 日 23:59。仍需真实的至少三次提交、版本发布、Pull Request、
个人 CSDN 博客、运行截图、完整演示视频和你自己的 PSP 表。

## 1. 在电脑运行并理解应用

项目根目录是同时包含 `server.py`、`README.md`、`addressbook/` 和 `static/` 的文件夹。
macOS 可先双击 `start.command`；首次运行需要联网安装依赖。也可以按 README
在终端创建 `.venv`、安装 requirements.txt 并执行 `python server.py`。

浏览器打开 `http://127.0.0.1:8080`。第一次应为空通讯录。点击 Import Excel，
下载 fictional sample 并手动导入，或自己添加虚构联系人。先检查以下内容：

1. 一个人能保存两个电话、两个邮箱以及其他类型，标签和值都显示完整。
2. 点击星标后进入 Bookmarks 可以找到该人，取消后从收藏视图消失。
3. Export Excel 下载 `.xlsx`，用 Excel/Numbers 打开确认为一人一行和明确列名。
4. 导入导出的文件能恢复信息，重复导入显示 skipped，不会重复增加相同记录。
5. 关闭并重启同一个数据库的服务后，联系人和收藏还在。

这些是你需要实际操作和理解的部分。使用 `docs/EVIDENCE_GUIDE.md` 的脚本录制。

## 2. 创建自己的 GitHub 仓库

在 GitHub 新建一个空的 Public 仓库，推荐名称：

`EE308FZ_Yihan_Wang_address_book`

因为本地已有 Git 历史，新建时不要再勾选初始化 README、`.gitignore` 或 License。
不要把之前的 Android 计算器仓库覆盖成通讯录。本地仓库名称也不代表 GitHub 已创建。

在项目根目录运行：

```bash
git status
git log --oneline --all --decorate
git remote -v
```

先检查真实分支和已有记录。`git remote -v` 为空时，添加远端：

```bash
git remote add origin https://github.com/3785107480/EE308FZ_Yihan_Wang_address_book.git
```

如果 origin 已存在，先核对地址，不要重复添加。推送需要通过你自己的 GitHub
身份验证；如果提示网页登录或令牌，请在本机完成，不要把令牌发进博客或聊天。

## 3. 保留真实提交并发起有内容的 PR

至少三次提交必须对应实际工作。当前历史以 `git log` 为准，不用空提交、修改日期、
伪造另一位成员来满足数量。你可以在 GitHub Commits 页面和本地记录中检查。

本地最后一批界面、部署和文档工作保存在 `feature/complete-address-book` 分支。
先检查 `git status` 和 `git log --oneline --all --decorate`。如果该分支已经有
第 3 次实际提交，直接推送已有的两个分支，不用重新创建分支或重复提交：

```bash
git push -u origin main
git push -u origin feature/complete-address-book
```

只有最后一批界面/文档工作确实尚未提交、功能分支也不存在时，才使用以下准备命令：

```bash
git switch -c feature/complete-address-book
git status
git add README.md static docs deploy .github package.json server.py start.command tests .gitignore addressbook
git diff --cached --stat
git commit -m "Complete address book interface and submission documentation"
git push -u origin main
git push -u origin feature/complete-address-book
```

执行前必须检查 `git status` 和暂存内容；目录中的实际文件可能已经被后续开发提交。
如果分支或提交已经存在，不要重复照抄。不要暂存真实联系人数据库、`.env`、密码或缓存。

在 GitHub 进入 Pull requests → New pull request：

- base 选 main。
- compare 选包含真实新增修改的功能分支。
- 查看 Files changed，确认能看到实际代码/文档差异。
- 标题说明具体功能；可用 `docs/PULL_REQUEST.md` 的英文草稿填写描述和真实验证结果。
- 点击 Create pull request，复制真实 PR 链接。
- 自己检查 Changes 和测试结果；确认后合并到 main，保留 PR 页面作为证据。

如果所有工作已经在 main，不要创建一个完全相同的分支冒充有内容的 PR。下一项
真实修正或文档完善在新分支提交，再发起 PR。原要求未指定必须向老师上游提交，
个人项目可采用本仓库功能分支到 main 的 PR；如老师另有通知，以通知为准。

完成合并后，同步本地并记录提交数量：

```bash
git switch main
git pull --ff-only origin main
git shortlog -sne --no-merges main
git rev-list --count --no-merges main
git rev-parse HEAD
```

博客中填写该分支的真实数值。Git author 可能显示 `3785107480`，这是你自己的 Git
身份，不要把同一个人的显示名和用户名当作两个成员。合并提交与代码提交分开说明。

## 4. 发布版本

在最终 PR 合并、README 可复现、所需验证完成后发布。GitHub 仓库 → Releases →
Draft a new release：

1. 选择或新建 `v1.0.0` 标签，目标为最终 main 提交。
2. 标题填写 `Yihan Wang Address Book v1.0.0`。
3. 参考 `docs/RELEASE_NOTES.md`，把真实验证结果和限制写进去。
4. 如有准备好的源码包可作为附件上传；GitHub 也会提供标签对应的源代码 ZIP。
5. Publish release，然后在未登录窗口打开并下载，检查是否包含全部运行文件。

博客写真实 release URL、版本和 commit SHA。标签存在不自动等于 release 页面已发布。

## 5. 可选公网部署加分

基础分不强制云部署，公网运行可争取额外 15 分。你已选择沿用阿里云
`8.217.14.75`。请使用 `deploy/EXISTING_SERVER_ZH.md`，为通讯录新增独立的
Gunicorn/systemd 服务和 Nginx 8081 站点。内部监听 `127.0.0.1:8080`，预期公网
地址为 `http://8.217.14.75:8081/`；只有从外网验证后才把它写成已上线地址。
数据库为 `/var/lib/yihan-addressbook/addressbook.db`。

2026 年 11 月 16 日的实际检查显示：Ubuntu 22.04、Python 3.10.12、Nginx 1.18；
旧计算器占用公网 80 和本机 8000，8080/8081 空闲，UFW 为 inactive。
你已安装 `python3-venv` 和 Git；代码上传、服务启用及外网验证仍需完成。
安全组仅需新增入方向 TCP 8081，不必公开内部 8080。

在 PR 合并后让服务器从 main 下载完整代码。不要把 SSH 私钥、登录密码或令牌贴到
博客。最终从手机移动网络打开公网地址并操作，不能用 `localhost`、本地预览或
仅有配置文件代替部署完成。

没有部署就如实在博客写未申请云部署加分。README 的部署方案本身不代表公网已上线。

## 6. 截图与完整视频

按 `docs/EVIDENCE_GUIDE.md` 拍摄最终版本。重点包括收藏、多种联系方式、实际 Excel
文件、导出后恢复、错误处理、持久化、真实 Git 历史、release 和 PR。

最新要求没有固定十张图门槛，但每张图都要有说明。完整运行视频必须能播放，
不能只有静态图片集。录制使用虚构联系人，并确保文字大小清楚。视频上传后用
未登录窗口测试播放，不要提供需要你个人网盘权限的链接。

## 7. 填写 PSP 和英文博客

`docs/BLOG_DRAFT.md` 是详细英文草稿。你需要补齐的真实信息：

- 新作业发布页 URL；这项无法从标题推断。
- 最终仓库、codestyle、release、PR、视频及可选公网 URL。
- 真实 Git 提交数量和最终 commit SHA。
- 自己实际投入的 PSP 时间，不能把助手运行分钟数当成人工工时。
- 自己实际参与、理解、调试和验证的经历。
- 最终测试结果，从 `docs/TEST_REPORT.md` 和实际命令核对，未完成不写通过。
- 对应图片和每张说明。

个人团队名可用 `Yihan Wang — Individual Project`。个人贡献写 100%，同时保留
AI 辅助的事实说明。没有队友就不用编造合作冲突、第二位贡献者和第二张 PSP 表。

## 8. 发布并提交

把完成的 Markdown 发布到 CSDN，按课程要求加入相应课程社区。检查目录每个链接、
图片、视频和外部地址。发布可能需要审核，提前操作。最后在作业提交渠道提交你自己
的博客链接，不是只保存草稿，也不是只提交 GitHub 链接。

最终截止：2026 年 11 月 17 日 23:59（北京时间）。班群最新通知也是要求的一部分。
