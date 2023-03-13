from users_gestion import add_new_user
from files_gestion import send_to, get_file
import json
import ftplib

with open("server_info.json") as my_file:
    json_str = my_file.read()

py_dict = json.loads(json_str)
type(py_dict)

# Server informations
S_host_n = py_dict["host_name"]
S_user_n = py_dict["username"]
S_psw    = py_dict["password"]

if __name__=='__main__':
    ftp = ftplib.FTP(S_host_n)
    ftp.login(user = S_user_n, passwd = S_psw)

    ftp.quit() 