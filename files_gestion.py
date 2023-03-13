import json
import ftplib
from rsa import rsa_enc, rsa_dec, rsa_sign, rsa_verify, h 
from Crypto.Cipher import AES
import os

from users_gestion import get_key

with open("server_info.json") as my_file:
    json_str = my_file.read()

py_dict = json.loads(json_str)

type(py_dict)

# Server informations
S_host_n = py_dict["host_name"]
S_user_n = py_dict["username"]
S_psw    = py_dict["password"]


def generate_key():
    return os.urandom(16)

#AES

def encrypt(message, key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return ciphertext, tag

def decrypt(ciphertext, tag, key):
    cipher = AES.new(key, AES.MODE_EAX, nonce=cipher.nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext

def send_to(sender, receptionist, file_name ):
    ftp = ftplib.FTP(S_host_n)
    ftp.login(user = S_user_n, passwd = S_psw)

    receptionist_public_key = get_key(receptionist)
    sender_public_key = get_key(sender)
    sender_private_key = 0 # get from test_password( local_psw)

    key = generate_key()
    enc_key = rsa_enc(key, receptionist_public_key)
    signature = rsa_sign(enc_key, sender_private_key)

    with open(file_name, "r") as file:
        message = file.read()
        ciphertext, tag = encrypt(message, key)
        with open("key_" + file_name, "w") as file2:
            file2.write("{\n\t\"sender\":" + sender  + ",\n\t\"key\":" + enc_key  + ",\n\t\"signature\":" + signature + ",\n\t\"tag\":" + tag + " \n}")
        with open("enc_" + file_name, "w") as file3:
            file3.write(ciphertext)
    ftp.cwd("./" + receptionist)

    add_file( ftp, "enc_" + file_name)
    add_file( ftp, "key_" + file_name)

    ftp.cwd("..")
    #test #rsa_verify(signature, sender_public_key)==h(m)

def get_file(file_name):
    my_private_key = 0 # get from test_password( local_psw)

    with open("key_" + file_name) as my_file:
        json_key = my_file.read()

    file_info_dict = json.loads(json_key)

    enc_key = file_info_dict["key"]
    signature = file_info_dict["signature"]
    sender_public_key = get_key(file_info_dict["sender"])
    tag = file_info_dict["tag"]

    if (rsa_verify(signature, sender_public_key) == h(enc_key)):
        print("code autentique")
        key = rsa_dec(enc_key,my_private_key)
        with open("enc_" + file_name, "r") as file:
            enc_message = file.read()
            dec_message = decrypt(enc_message.encode() , tag, key)
            with open(file_name, "w") as file2:
                file2.write(dec_message.decode())
    else :
        print("message non authentique " )
    
   

