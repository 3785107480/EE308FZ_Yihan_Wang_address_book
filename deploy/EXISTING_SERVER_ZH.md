# 沿用已有阿里云服务器部署通讯录

适用服务器：之前计算器使用的 `8.217.14.75`。以下是待执行步骤，
不是已部署成功的记录。当前开发环境无法通过 SSH 连接这台服务器。

本方案为通讯录增加独立的服务、目录和端口。预期公开地址是
`http://8.217.14.75:8081/`，只有实际部署并从外网验证后才能填入博客。
原计算器继续使用端口 80 和内部端口 8000；通讯录内部使用 8080，
Nginx 公开使用 8081。不要覆盖原计算器的数据库或 Nginx 配置。

## 1. 登录并检查服务器

在阿里云控制台找到这台实例，选择「远程连接 / Workbench」，用自己的
服务器账号登录。不要把密码或私钥发到聊天或提交到 GitHub。

先执行只读检查：

```bash
sudo ss -ltnp
sudo systemctl status orbit-calculator --no-pager
sudo ls -l /etc/nginx/sites-enabled
curl --fail http://127.0.0.1/api/health
```

确认 8080、8081 尚未占用。若占用，先查明进程，不要停止未知服务。
本文仅适用于这两个端口空闲的情况。记录原计算器 health 结果，部署后对比。

## 2. 安装运行环境并下载已发布代码

先按 `docs/NEXT_STEPS_ZH.md` 把代码推送到自己的 GitHub 仓库，再执行：

```bash
sudo apt update
sudo apt install -y python3 python3-venv nginx git
```

检查服务账号：

```bash
id addressbook
```

只有提示不存在时才创建：

```bash
sudo useradd --system --user-group --home-dir /opt/yihan-addressbook --shell /usr/sbin/nologin addressbook
```

确认 `/opt/yihan-addressbook` 不存在后克隆。若已存在，先检查目录内容，
不要用删除、强制覆盖命令处理已有数据：

```bash
sudo git clone https://github.com/3785107480/EE308FZ_Yihan_Wang_address_book.git /opt/yihan-addressbook
cd /opt/yihan-addressbook
sudo python3 -m venv .venv
sudo .venv/bin/python -m pip install -r requirements.txt
sudo .venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

测试只使用临时数据库。若失败，先解决并保留实际结果，不要写全部通过。

## 3. 启用通讯录独立服务

先确认没有同名的其他服务，再安装本项目服务：

```bash
sudo cp deploy/addressbook.service /etc/systemd/system/addressbook.service
sudo systemctl daemon-reload
sudo systemctl enable --now addressbook
sudo systemctl status addressbook --no-pager
curl --fail http://127.0.0.1:8080/api/health
```

成功响应包含 `"status":"ok"` 和 `"version":"1.0.0"`。
systemd 自动创建可写的数据目录。实际数据库位于
`/var/lib/yihan-addressbook/addressbook.db`，与计算器的数据库无关。

## 4. 增加 Nginx 8081 站点

确认目标文件和链接名未被其他站点使用，然后执行：

```bash
sudo cp deploy/addressbook-shared.nginx /etc/nginx/sites-available/yihan-addressbook
sudo ln -s /etc/nginx/sites-available/yihan-addressbook /etc/nginx/sites-enabled/yihan-addressbook
sudo nginx -t
```

只有 `nginx -t` 成功后才重载：

```bash
sudo systemctl reload nginx
curl --fail http://127.0.0.1:8081/api/health
curl --fail http://127.0.0.1/api/health
```

最后一条同时检查原计算器。不要禁用原站点，也不需要禁用 default。
共享站点保留 Host 中的端口，避免浏览器的同源写请求因端口不一致被拒绝。

## 5. 在阿里云允许公开访问

在实例对应的安全组或轻量服务器防火墙中增加入站 TCP `8081`，
来源为 `0.0.0.0/0`。若服务器启用了 UFW，先查看状态：

```bash
sudo ufw status
```

仅当状态是 active 时增加：

```bash
sudo ufw allow 8081/tcp
```

无需向公网开放内部端口 8080。保持当前 SSH 登录规则和原服务规则。

## 6. 从外网验证

用手机移动网络打开：

```text
http://8.217.14.75:8081/
http://8.217.14.75:8081/api/health
```

完成添加虚构联系人、收藏、多个联系方式、Excel 导出和导入，
刷新页面验证记录保留。截取包含公开地址栏的图片，并录制完整演示。
验证通过后才在博客的 Public application URL 中填写实际地址。

公开演示使用共享通讯录和 HTTP，请使用虚构联系人。原型不提供各用户独立数据。
如启用可选访问密码，应先配置 HTTPS，并把评估凭据私下交给老师。

## 7. 故障与后续维护

```bash
sudo journalctl -u addressbook -n 80 --no-pager
sudo nginx -t
sudo ss -ltnp
```

更新源代码时保留数据库。评估期间保持服务器和服务可用。
服务文件可设为开机启动，但这不能保证订阅到期或服务器关机后仍能访问。
