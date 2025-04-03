## 4. 创建环境变量

确保已安装 unzip 工具

```bash
sudo apt update
sudo apt install unzip
```

解压环境变量

```bash
cd code/backend/model
unzip env.zip
ls -a
```

## 5. 测试启动后端服务

使用 `python3` 启动 FastAPI 后端服务，建议在测试模式下运行，绑定到所有网络接口：

```bash
cd RAGnition
python3 -m venv venv
source venv/bin/activate
```

```bash
cd code
python -m backend.main
```

然后在浏览器或使用 `curl` 访问 `http://<你的服务器IP>:8536/api/v1/files/list`，检查接口是否正常响应。

```bash
curl http://0.0.0.0:8536/api/v1/files/list
curl http://20.189.123.18:8536/api/v1/files/list
```

## 6. 配置 systemd 服务（可选，便于后台运行）

在 `/etc/systemd/system/` 目录下创建 `ragnition.service` 文件：

```bash
sudo nano /etc/systemd/system/ragnition.service
```

文件内容如下（请替换路径和用户名）：

```ini
[Unit]
Description=RAGnition 后端服务
After=network.target

[Service]
User=rocky
WorkingDirectory=/home/rocky/project/RAGnition/code
# 使用虚拟环境内的 Python 解释器运行后端模块
ExecStart=/home/rocky/project/RAGnition/venv/bin/python -m backend.main
Restart=always

[Install]
WantedBy=multi-user.target
```

保存后，加载并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable ragnition.service
sudo systemctl start ragnition.service
```

检查服务状态：

```bash
sudo systemctl status ragnition.service
```

## 7. 配置 Nginx 反向代理（可选）

如果希望使用标准端口（如 `80/443`）访问后端，可以安装 Nginx 并配置反向代理：

```bash
sudo apt install -y nginx
```

创建或编辑 Nginx 配置文件（例如 `/etc/nginx/sites-available/nginxapp`）：

```nginx
server {
    listen 80;
    server_name 20.189.123.18;

    location /ragnition/ {
        proxy_pass http://127.0.0.1:8536/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /gamestar/ {
        proxy_pass http://127.0.0.1:8521/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

启用该配置并重启 Nginx：

```bash
sudo rm /etc/nginx/sites-enabled/nginxapp
sudo ln -s /etc/nginx/sites-available/nginxapp /etc/nginx/sites-enabled/nginxapp
sudo nginx -t
sudo systemctl restart nginx
```

## 8. 防火墙配置

确保服务器防火墙允许 SSH（22）、HTTP（80）、HTTPS（443）以及后端服务端口（如 `8536`）：

```bash
sudo ufw enable
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8536
```

## 9. 更新代码

直接更新git仓库即可，服务会自动重启。或者使用下面命令来确保服务重启：
```bash
sudo systemctl status ragnition.service
sudo systemctl restart ragnition.service
sudo systemctl status ragnition.service
```

### HTTPS加密

github page强制使用https，因此服务器上面需要安装Cloudflare，并且申请Cloudflare Named Tunnel，最终实现对外使用https的能力。

```bash
screen -S ragnitiontunnel
cloudflared tunnel --url http://localhost:8536
```

每一次生成的域名是随机的，比如

```bash
curl https://ipaq-brass-patch-travis.trycloudflare.com/api/v1/files/list
```

断开会话但进程不会停止

```bash
Ctrl + A, 然后按 D
```

重新连接会话

```bash
screen -r ragnitiontunnel
```