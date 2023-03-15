import json
import ftplib
from rsa import gen_rsa_keypair
import hashlib
import getpass
from cryptography.fernet import Fernet
import base64
import os

bits = 1024 # RSA keys size

""" Puts files in server """
def add_file(ftp, file_name):
    with open(file_name, "rb") as file:
        ftp.storbinary("STOR " + file_name, file)

def delete_file(ftp, file_name):
    ftp.delete(file_name) # delete file

""" Returns user dictionary"""
def get_user_dictionary():
    with open("users.json") as my_file:
        json_dict = my_file.read()

    user_dict = json.loads(json_dict)
    #print(user_dict)
    return user_dict

""" Encrypt and store private key 
    - first hash to check password 
    - second one is the key to encrypt private key
"""
def keep_private_key(user_name, local_psw, private_key):
    hash1 = hashlib.sha256(local_psw.encode())
    hash2 = hashlib.sha1(local_psw.encode())

    # Store the hash of the master password in a file named local.txt
    with open("./local_autentification/" + user_name + "/local.txt", "w") as f:
        f.write(hash2.hexdigest())

    # Create a Fernet object for encrypting/decrypting
    f = Fernet(base64.b64encode(hash1.digest()[:32]))

    # Encrypt the protected password
    encrypted_password = f.encrypt(str(private_key).encode("utf-8"))

    # Store the encrypted password in a file named private_key.txt
    with open("./local_autentification/" + user_name + "/private_key.txt", "wb") as f:
        f.write(encrypted_password)

    print("Password protected and stored successfully!")

""" Test if the pssword is correct and returns unencrypted private key"""
def test_password(user_name, local_psw):
    hash1 = hashlib.sha256(local_psw.encode())
    hash2 = hashlib.sha1(local_psw.encode())

    # Get the hash of the master password from the local.txt file
    with open("./local_autentification/" + user_name + "/local.txt", "r") as f:
        code = f.read().strip()
        if code == hash2.hexdigest():
            # Get the encrypted password from the private_key.txt file
            with open("./local_autentification/" + user_name + "/private_key.txt", "rb") as f2:
                encrypted_password = f2.read().strip()
                # Create a Fernet object for encrypting/decrypting
                fer = Fernet(base64.b64encode(hash1.digest()[:32]))
                decrypted_password = fer.decrypt(encrypted_password)

                return get_key_from_str(decrypted_password.decode("utf-8"))
        else:
            print("Error: Wrong password.")



""" Create new user :
        - generates rsa key and store it
        - create user folder
"""
def add_new_user(ftp, name, local_psw ):
    filename = "users.json"
    if not os.path.exists("./local_autentification"):
            os.makedirs("./local_autentification")

    if filename in ftp.nlst():                                  # check if users.json exists

        with open(filename, 'wb') as fichier_local:             # get files from server
            ftp.retrbinary('RETR ' + filename, fichier_local.write)
        users_dictionary = get_user_dictionary()                # get dictionary
        if name in users_dictionary:
            print("Error: A user already exists with this name.")
            return
        public_key, private_key = gen_rsa_keypair( bits )       # generate RSA keys
        if not os.path.exists("./local_autentification/" + name):
            os.makedirs("./local_autentification/" + name)
        keep_private_key( name, local_psw, private_key)         # encrypt private key and store it
        add_user_in_file( ftp, filename, name, str(public_key)) # add user in the file (name + public key)
        ftp.mkd(name)                                           # create user folder

    else:
        public_key, private_key = gen_rsa_keypair( bits )
        if not os.path.exists("./local_autentification/" + name):
            os.makedirs("./local_autentification/" + name)
        keep_private_key( name, local_psw, private_key)
        create_user_file( ftp, filename, name, str(public_key))
        ftp.mkd(name)
    #ftp.quit()  

""" Adds user on existing file """
def add_user_in_file( ftp, filename, name, public_key):
    with open(filename, 'rb') as file:
        lines = file.readlines()
        lines.pop()             # Removes last line
        new_line = ("\t,\"" + name + "\":\""+ public_key + "\"\n}").encode('utf-8')
        lines.append(new_line)
    with open(filename, 'wb') as file:
        file.writelines(lines)
    add_file( ftp, filename)    # Puts new file on server

""" Creates file and adds user """
def create_user_file( ftp, filename, name, public_key):
    with open(filename, "w") as new_file:
        new_file.write("{\n\t\"" + name + "\":\""+ public_key + "\"\n}")
    add_file( ftp, filename)

"""Removes user from server !!! does not remove his folder !!!"""
def remove_user (ftp, name):
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
            complete_name = "\""+name+"\""
            for i in range(len(lines)):     # Removes line with user name on it
                if complete_name in lines[i]:
                    del lines[i]
                    break
        # Rewrite local file
        with open(filename, 'w') as file:
            file.writelines(lines) 
        add_file( ftp, filename)
    else:
        print("Error: user doesn't exist. ")
        return

""" Returns user public key"""
def get_key (user):
    dico = get_user_dictionary()
    string = dico[user]
    return get_key_from_str(string)
    
""" Returns tuple from string """
def get_key_from_str(key_string):
    characters = "()"
    key_string = ''.join( x for x in key_string if x not in characters)
    e, n = key_string.split(',')
    e = int(e)
    n = int(n)
    return (e,n)
