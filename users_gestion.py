import json
import ftplib
from rsa import gen_rsa_keypair
import hashlib
import getpass
from cryptography.fernet import Fernet
import base64

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

def keep_private_key( local_psw, private_key):
    hash1 = hashlib.sha256(local_psw.encode())
    hash2 = hashlib.sha1(local_psw.encode())
    print(hash1.hexdigest())
    print(hash2.hexdigest())

    # Stocker le hash du mot de passe principal dans un fichier principal.txt
    with open("./local_autentification/local.txt", "w") as f:
        f.write(hash2.hexdigest())

    # Créer un objet Fernet pour encrypter/décrypter
    f = Fernet(base64.b64encode(hash1.digest()[:32]))

    # Encrypter le mot de passe protégé
    encrypted_password = f.encrypt(private_key.encode("utf-8"))

    # Stocker le mot de passe encrypté dans un fichier password.txt
    with open("./local_autentification/private_key.txt", "wb") as f:
        f.write(encrypted_password)

    print("Mot de passe protégé stocké avec succès!")

def test_password( local_psw):
    hash1 = hashlib.sha256(local_psw.encode())
    hash2 = hashlib.sha1(local_psw.encode())
    print(hash1.hexdigest())
    print(hash2.hexdigest())

    # Stocker le hash du mot de passe principal dans un fichier principal.txt
    with open("./local_autentification/local.txt", "r") as f:
        code = f.read().strip()
        if code == hash2.hexdigest() :
            with open("./local_autentification/private_key.txt", "rb") as f2:
                encrypted_password = f2.read().strip()
                # Créer un objet Fernet pour encrypter/décrypter
                fer = Fernet(base64.b64encode(hash1.digest()[:32]))
                decrypted_password = fer.decrypt(encrypted_password)
                #print("aaaaa")
                print(decrypted_password.decode("utf-8"))
                return decrypted_password.decode("utf-8")

        else : 
            print("Error: Wrong password.")


bits = 128
#create new user
def add_new_user( name, local_psw ):
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
      
        public_key, private_key = gen_rsa_keypair( bits )
        keep_private_key( local_psw, private_key)
        add_user_in_file( ftp, filename, name, str(public_key))

    else:
        public_key, private_key = gen_rsa_keypair( bits )
        keep_private_key( local_psw, private_key)
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

def remove_user (name):
    ftp = ftplib.FTP(S_host_n)
    ftp.login(user = S_user_n, passwd = S_psw)

    filename = "users.json"

    if filename in ftp.nlst():
        #get file from server
        with open(filename, 'wb') as fichier_local:
            ftp.retrbinary('RETR ' + filename, fichier_local.write)

        # get dictionary
        users_dictionary = get_user_dictionary()
        if name not in users_dictionary:
            print("Error: user doesn't exist. ")
            return


        with open(filename, 'r') as file:
            lines = file.readlines()
            
            #trouver l'utilisateur envoyer son index
            #suprimer de la liste la ligne
            complete_name = "\""+name+"\""
            for i in range(len(lines)):
                if complete_name in lines[i]:
                    print(lines[i])
                    print(lines)
                    del lines[i]
                    print(lines)
                    break
        # Écrire le fichier mis à jour localement
        with open(filename, 'w') as file:
            file.writelines(lines) 
        add_file( ftp, filename)

    else:
        print("Error: user doesn't exist. ")
        return

    ftp.quit()  

def get_key (user):
    dico = get_user_dictionary()
    string = dico[user]
    characters = "()"
    string = ''.join( x for x in string if x not in characters)
    e, n = string.split(',')
    e = int(e)
    n = int(n)
    return e,n

"""
remove_user ("po")
keep_private_key( "local_psw", "private_key")
test_password( "local_psw")"""
#int(dico["po"])
#delete_file("users.json")
#add_file( "users.json")