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



def add_file( file_name):
    ftp = ftplib.FTP(S_host_n)
    ftp.login(user = S_user_n, passwd = S_psw)
    with open(file_name, "rb") as file:
        ftp.storbinary("STOR " + file_name, file)
    ftp.quit() 

#delete file
def delete_file( file_name):
    #supprimer un fichier
    ftp = ftplib.FTP(S_host_n)
    ftp.login(user = S_user_n, passwd = S_psw)

    ftp.cwd(".") # changez le chemin vers le répertoire contenant votre fichier
    ftp.delete(file_name)
    ftp.quit() 



delete_file("users.json")
#add_file( "users.json")