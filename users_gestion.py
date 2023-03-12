import json
import ftplib
from rsa import gen_rsa_keypair

with open("server_info.json") as my_file:
    json_str = my_file.read()

py_dict = json.loads(json_str)

type(py_dict)

# Server informations
S_host_n = py_dict["host_name"]
S_user_n = py_dict["username"]
S_psw    = py_dict["password"]



def add_file(ftp, file_name):
    with open(file_name, "rb") as file:
        ftp.storbinary("STOR " + file_name, file)

#delete file
def delete_file( file_name):
    #supprimer un fichier
    ftp = ftplib.FTP(S_host_n)
    ftp.login(user = S_user_n, passwd = S_psw)

    ftp.cwd(".") # changez le chemin vers le répertoire contenant votre fichier
    ftp.delete(file_name)
    ftp.quit() 

def get_user_dictionary():
    with open("users.json") as my_file:
        json_dict = my_file.read()

    user_dict = json.loads(json_dict)
    #print(user_dict)
    return user_dict

bits = 128
#create new user
def add_new_user( name ):
    ftp = ftplib.FTP(S_host_n)
    ftp.login(user = S_user_n, passwd = S_psw)

    filename = "users.json"

    if filename in ftp.nlst():
        #get file from server
        with open(filename, 'wb') as fichier_local:
            ftp.retrbinary('RETR ' + filename, fichier_local.write)

        # get dictionary
        users_dictionary = get_user_dictionary()
        if name in users_dictionary:
            print("Error: A user already exists with this name.")
            return

        # créé la clé
        public_key, private_key = gen_rsa_keypair( bits )
        add_user_in_file( ftp, filename, name, str(public_key))

    else:
        # créé la clé
        public_key, private_key = gen_rsa_keypair( bits )
        create_user_file( ftp, filename, name, str(public_key))

    ftp.quit()  


def add_user_in_file( ftp, filename, name, public_key):
    with open(filename, 'rb') as file:
        lines = file.readlines()
        # Supprimer la dernière ligne
        lines.pop()
        
        # Ajouter une nouvelle ligne
        new_line = ("\t,\"" + name + "\":\""+ public_key + "\"\n}").encode('utf-8')
        lines.append(new_line)
    # Écrire le fichier mis à jour localement
    with open(filename, 'wb') as file:
        file.writelines(lines)

    add_file( ftp, filename)

def create_user_file( ftp, filename, name, public_key):
    with open(filename, "w") as new_file:
        new_file.write("{\n\t\"" + name + "\":\""+ public_key + "\"\n}")
    add_file( ftp, filename)

#add_new_user( "po")


def get_key (user):
    dico = get_user_dictionary()
    string = dico[user]
    characters = "()"
    string = ''.join( x for x in string if x not in characters)
    e, n = string.split(',')
    e = int(e)
    n = int(n)
    return e,n

#int(dico["po"])
#delete_file("users.json")
#add_file( "users.json")