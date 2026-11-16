# Deploy to a new Ubuntu cloud server

The optional bonus requires a publicly reachable **running application**. Providing
these files, a local preview or an unstarted virtual machine does not earn it.
The student has chosen to reuse the older Alibaba Cloud server. Follow
[the existing-server guide](EXISTING_SERVER_ZH.md) for that case; the steps below
are for a fresh dedicated host only.

## 1. Prepare the host

Suggested: Alibaba Cloud ECS/Lightweight Application Server or equivalent, Ubuntu
22.04/24.04 LTS, 1–2 vCPUs, 2 GiB RAM, 20 GiB disk, public IPv4. Use SSH key login.
Allow inbound TCP 80 for the app, 443 if using HTTPS, and restrict SSH 22 to your
own IP where possible. This is a browser application; no Android SDK is required.

On the server terminal, run:

```bash
sudo apt update
sudo apt install -y python3 python3-venv nginx git
sudo useradd --system --user-group --home-dir /opt/yihan-addressbook --shell /usr/sbin/nologin addressbook
```

Run the user creation only if the `addressbook` account does not yet exist.

## 2. Copy source and install dependencies

Once the student has published the GitHub repository:

```bash
sudo git clone https://github.com/3785107480/EE308FZ_Yihan_Wang_address_book.git /opt/yihan-addressbook
sudo python3 -m venv /opt/yihan-addressbook/.venv
sudo /opt/yihan-addressbook/.venv/bin/python -m pip install -r /opt/yihan-addressbook/requirements.txt
```

Run the test command from `/opt/yihan-addressbook`, so the package import resolves:

```bash
cd /opt/yihan-addressbook
sudo .venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

If you upload a release ZIP instead, extract it into `/opt/yihan-addressbook` so
that `wsgi.py`, `static/` and `addressbook/` are directly inside that folder.
The directory should not contain a second nested copy of the repository.

## 3. Enable the service and reverse proxy

```bash
sudo cp /opt/yihan-addressbook/deploy/addressbook.service /etc/systemd/system/addressbook.service
sudo cp /opt/yihan-addressbook/deploy/addressbook.nginx /etc/nginx/sites-available/yihan-addressbook
sudo ln -s /etc/nginx/sites-available/yihan-addressbook /etc/nginx/sites-enabled/yihan-addressbook
sudo systemctl daemon-reload
sudo systemctl enable --now addressbook
sudo nginx -t
sudo systemctl reload nginx
```

On a **fresh dedicated server**, the Nginx default site may intercept requests.
Inspect enabled sites with `ls -l /etc/nginx/sites-enabled`. If `default` is only
the unused welcome page, disable that symlink:

```bash
sudo unlink /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

Do not disable another application’s site. Do not run `ln -s` again if the intended
symlink already exists. The service uses systemd StateDirectory to create the
writable database directory; application source can remain root-owned/read-only.

## 4. Verify local and public access

```bash
curl --fail http://127.0.0.1:8080/api/health
curl --fail http://127.0.0.1/api/health
sudo systemctl status addressbook --no-pager
```

Expected health JSON: `{"status":"ok","version":"1.0.0"}` (spacing may vary).

Open `http://YOUR_PUBLIC_IP/` from another network, such as a phone using mobile
data. Open `/api/health` too. Add a fictional contact, bookmark it, enter multiple
methods, export/import XLSX, reload the browser and verify persistence. Record
the public URL and take screenshots with the address bar visible. Keep the service
and server subscription active throughout assessment.

## 5. Optional HTTPS and access gate

Cloud hosting earns the optional deployment category; a domain is not mandatory.
For HTTPS, point a domain to the server, replace `server_name _;` with that domain,
install Certbot using the current official Ubuntu instructions, and issue a
certificate for the Nginx site. Verify certificate renewal.

The application supports `ADDRESSBOOK_PASSWORD` as an optional environment variable.
To enable it, create `/etc/yihan-addressbook.env` using `sudoedit`, enter
`ADDRESSBOOK_PASSWORD=` followed by a strong password, set file permissions to 600,
and restart the service. Username is `reviewer`. Use this gate over HTTPS only and
share the evaluation password privately. Do not put secrets in Git, screenshots or
the blog. If no password is enabled, publish fictional data only and explain that
the demo is shared and writable.

## 6. Diagnose, back up and update

```bash
sudo journalctl -u addressbook -n 80 --no-pager
sudo nginx -t
```

The live database is `/var/lib/yihan-addressbook/addressbook.db`, outside the source
checkout. For a consistent backup, stop the service, copy that exact file to a safe
private backup location and restart the service. Do not upload a database containing
personal data to GitHub.

Update source through Git or a reviewed release, reinstall changed requirements,
run tests, restart `addressbook`, and recheck the health endpoint. Do not overwrite
the live database with an empty development database.
