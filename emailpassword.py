
def email_password() :
    ep_dict = []
    ep_file = open("emailpassword3.txt", "r+")
    while True :
        lines = ep_file.readline()
        split = lines.split(":")
        if not lines :
            break
        ep_dict.append({"email" : split[0], "password" : split[1].replace("\n","")})
        #print(ep_dict)
    ep_file.close()
    return ep_dict

# email_password()