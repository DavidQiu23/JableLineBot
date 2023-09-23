## 指令

- 義旻我要發燒列車
- 義旻我要最新的車
- 義旻我要 {名子} 的車
- ~~除此之外以chatGPT回覆~~ chatGPT API 免費試用期已過

## 筆記
### 無頭模式並且指定user-agent並且每次呼叫就重新開啟一次driver，才能騙過cloudflare
### Ngnix
```
sudo apt-get install nginx  --安裝
sudo service nginx restart  --重啟指令
```
設定位置：/etc/nginx/sites-available/default
```
location / {
    proxy_set_header     X-Forwarded-Host $host;
    proxy_set_header     X-Forwarded-Server $host;
    proxy_set_header     X-Real-IP $remote_addr;
    proxy_set_header     Host $host;
    proxy_set_header     X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_pass           http://127.0.0.1:5000;
}
```
### SSL
```
$ apt-get update
$ sudo apt-get install certbot
$ apt-get install python3-certbot-nginx
```
- No-IP (https://davidqiu.ddns.net/)
- 目前架設在樹莓派，使用ngnix,uWSGI
- 啟動指令 `uwsgi --ini uwsgi.ini`