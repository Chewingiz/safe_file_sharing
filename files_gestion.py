import json
import ftplib
import base64
from rsa import rsa_enc, rsa_dec, rsa_sign, rsa_verify, h, gen_rsa_keypair 
import os
import ast
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from users_gestion import get_key, add_file

def generate_key():
    return os.urandom(16)

#AES
def encrypt(message, key):
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    padded_message = pad(message, AES.block_size, style='pkcs7')
    ciphertext, tag = cipher.encrypt_and_digest(padded_message)
    return (ciphertext, iv, tag)

def decrypt(ciphertext, tag, key, iv):
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    padded_plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    plaintext = unpad(padded_plaintext, AES.block_size, style='pkcs7')
    return plaintext


def send_to(ftp, sender, sender_private_key, receptionist, receptionist_private_key, file_name ):

    receptionist_public_key = get_key(receptionist)

    sender_public_key = get_key(sender)

    key = generate_key()
    enc_key = rsa_enc( repr(key), receptionist_public_key)
    signature = rsa_sign(enc_key, sender_private_key)
    key2 = rsa_dec(enc_key, receptionist_private_key)

    with open(file_name, "rb") as file:
        message = file.read()
        #(type(message))
        ciphertext, iv, tag = encrypt(message, key)

   
        with open("key_" + file_name, "w") as file2:
            file2.write("{\n\t\"sender\":\"" + sender  + "\",\n\t\"key\":\"" + str(enc_key)  + "\",\n\t\"iv\":\"" + str(base64.b64encode(iv).decode('utf-8'))  + "\",\n\t\"signature\":\"" + str(signature) + "\",\n\t\"tag\":\"" + str(base64.b64encode(tag).decode('utf-8')) + "\" \n}")
        with open("enc_" + file_name, "wb") as file3:

            file3.write(ciphertext)
    ftp.cwd("./" + receptionist)
    add_file( ftp, "enc_" + file_name)
    add_file( ftp, "key_" + file_name)
    ftp.cwd("..")

def get_file(ftp,name, my_private_key, file_name):
    ftp.cwd("./" + name)
    with open("enc_" + file_name, 'wb') as fichier_local:
        ftp.retrbinary('RETR ' + "enc_" + file_name, fichier_local.write)
    with open("key_" + file_name, 'wb') as fichier_local:
        ftp.retrbinary('RETR ' + "key_" + file_name, fichier_local.write)
    ftp.cwd("..")
    with open("key_" + file_name) as my_file:
        json_key = my_file.read()

    file_info_dict = json.loads(json_key)

    enc_key = int(file_info_dict["key"])
    signature = int(file_info_dict["signature"])
    sender_public_key = get_key(file_info_dict["sender"])
    tag =  base64.b64decode(file_info_dict["tag"])
    iv = base64.b64decode(file_info_dict["iv"])


    if (rsa_verify(signature, sender_public_key) == h(enc_key)):
        print("code autentique")
        key = ast.literal_eval(rsa_dec(enc_key, my_private_key))

        with open("enc_" + file_name, "rb") as file:
            enc_message = file.read()

            dec_message = decrypt(enc_message, tag, key, iv).decode()
            with open("dec_" + file_name, "w") as file2:
                file2.write(dec_message)
    else :
        print("message non authentique " )