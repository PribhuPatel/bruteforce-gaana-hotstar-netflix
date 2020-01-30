from httplib2 import socks

def socks4_proxy() :
    socks4_dict = []
    socks4_file = open("socks4.txt","r+")     
    while True :
        line = socks4_file.readline()
        remove_n = line.strip()
        portsplit = remove_n.split(":")
        if not line:
            break
        socks4_dict.append({"proxy":portsplit[0] , "port":int(portsplit[1]), "type":socks.PROXY_TYPE_SOCKS4, "working" : 1 , "count" : 0})
       # print(socks4_dict)
       
    socks4_file.close()
    return socks4_dict

def socks5_proxy() :
    socks5_dict = []
    socks5_file = open("socks5.txt","r+")     
    while True :
        line = socks5_file.readline()
        remove_n = line.strip()
        portsplit = remove_n.split(":")
        if not line:
            break
        socks5_dict.append({"proxy":portsplit[0] , "port":int(portsplit[1]), "type":socks.PROXY_TYPE_SOCKS5, "working" : 1 , "count" : 0})
      #  print(socks5_dict)
    socks5_file.close()
    return socks5_dict

def htttp_proxy() :
    http_dict = []
    http_file = open("http.txt","r+") 
    while True :
        line = http_file.readline()
        remove_n = line.strip()
        portsplit = remove_n.split(":")
        if not line:
            break
        http_dict.append({"proxy":portsplit[0] , "port":int(portsplit[1]), "type":socks.PROXY_TYPE_HTTP, "working" : 1 , "count" : 0,"user":portsplit[2],"pass":portsplit[3]})
        #http_dict.append({"proxy":remove_n , "port":22225, "type":socks.PROXY_TYPE_HTTP, "working" : 1 , "count" : 0})
       
       # print(http_dict)
    http_file.close()
    return http_dict

# __name__ = "proxydictionary"
# socks4_proxy()
# socks5_proxy()
# htttp_proxy()
