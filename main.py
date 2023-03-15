from users_gestion import add_new_user, delete_file, test_password
from files_gestion import send_to, get_file
import json
import ftplib

with open("server_info.json") as my_file:
    json_str = my_file.read()

py_dict = json.loads(json_str)
type(py_dict)

# Server informations
S_host_n = py_dict["host_name"]
S_port   = int(py_dict["port"])
S_user_n = py_dict["username"]
S_psw    = py_dict["password"]

if __name__=='__main__':
    ftp = ftplib.FTP()
    ftp.connect(S_host_n, S_port)
    ftp.login(user = S_user_n, passwd = S_psw)
    print("OK")
    
    
    #Reinit for tests
    #delete_file(ftp,"users.json") 
    #print("OK")
    add_new_user(ftp, "Beatrice", "MotDePasse123")
    #print("OK")
    add_new_user(ftp, "Anais", "MotDePasse")
    #print("OK")

    #log in
    Anais_private_key = test_password("Anais", "MotDePasse")
    #print("OK")
    Beatrice_private_key = test_password("Beatrice", "MotDePasse123")
    #print("OK")


    send_to(ftp, "Anais", Anais_private_key, "Beatrice", "test.txt")
   # print("OK")
    get_file(ftp,"Beatrice", Beatrice_private_key, "test.txt")

    ftp.quit() 

    