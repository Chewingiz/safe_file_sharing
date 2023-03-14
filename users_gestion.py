import json
import ftplib
from rsa import gen_rsa_keypair
import hashlib
import getpass
from cryptography.fernet import Fernet
import base64
import os

bits = 2048

def add_file(ftp, file_name):
    with open(file_name, "rb") as file:
        ftp.storbinary("STOR " + file_name, file)

#delete file
def delete_file(ftp, file_name):
    #supprimer un fichier
    ftp.delete(file_name)
    #ftp.quit() 

def get_user_dictionary():
    with open("users.json") as my_file:
        json_dict = my_file.read()

    user_dict = json.loads(json_dict)
    #print(user_dict)
    return user_dict

def keep_private_key(user_name, local_psw, private_key):
    hash1 = hashlib.sha256(local_psw.encode())
    hash2 = hashlib.sha1(local_psw.encode())
    #print(hash1.hexdigest())
    #print(hash2.hexdigest())

    # Stocker le hash du mot de passe principal dans un fichier principal.txt
    with open("./local_autentification/" + user_name + "/local.txt", "w") as f:
        f.write(hash2.hexdigest())

    # Créer un objet Fernet pour encrypter/décrypter
    f = Fernet(base64.b64encode(hash1.digest()[:32]))

    # Encrypter le mot de passe protégé
    encrypted_password = f.encrypt(str(private_key).encode("utf-8"))

    # Stocker le mot de passe encrypté dans un fichier password.txt
    with open("./local_autentification/" + user_name + "/private_key.txt", "wb") as f:
        f.write(encrypted_password)

    print("Mot de passe protégé stocké avec succès!")

def test_password( user_name, local_psw):
    hash1 = hashlib.sha256(local_psw.encode())
    hash2 = hashlib.sha1(local_psw.encode())
    #print(hash1.hexdigest())
    #print(hash2.hexdigest())

    # Stocker le hash du mot de passe principal dans un fichier principal.txt
    with open("./local_autentification/" + user_name + "/local.txt", "r") as f:
        code = f.read().strip()
        if code == hash2.hexdigest() :
            with open("./local_autentification/" + user_name + "/private_key.txt", "rb") as f2:
                encrypted_password = f2.read().strip()
                # Créer un objet Fernet pour encrypter/décrypter
                fer = Fernet(base64.b64encode(hash1.digest()[:32]))
                decrypted_password = fer.decrypt(encrypted_password)

                #print(type(decrypted_password.decode("utf-8")))
                return get_key_from_str(decrypted_password.decode("utf-8"))

        else : 
            print("Error: Wrong password.")



#create new user
def add_new_user(ftp, name, local_psw ):
    """ftp = ftplib.FTP(S_host_n)
    ftp.login(user = S_user_n, passwd = S_psw)"""

    filename = "users.json"
    if not os.path.exists("./local_autentification"):
            os.makedirs("./local_autentification")

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

        if not os.path.exists("./local_autentification/" + name):
            os.makedirs("./local_autentification/" + name)

        keep_private_key( name, local_psw, private_key)
        add_user_in_file( ftp, filename, name, str(public_key))
        ftp.mkd(name)

    else:
        public_key, private_key = gen_rsa_keypair( bits )

        if not os.path.exists("./local_autentification/" + name):
            os.makedirs("./local_autentification/" + name)

        keep_private_key( name, local_psw, private_key)
        create_user_file( ftp, filename, name, str(public_key))
        ftp.mkd(name)
    #ftp.quit()  


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
                    del lines[i]
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
    return get_key_from_str(string)
    

def get_key_from_str(key_string):
    characters = "()"
    key_string = ''.join( x for x in key_string if x not in characters)
    e, n = key_string.split(',')
    e = int(e)
    n = int(n)
    return (e,n)
"""
remove_user ("po")
keep_private_key( "local_psw", "private_key")
test_password( "local_psw")"""
#int(dico["po"])
#delete_file("users.json")
#add_file( "users.json")