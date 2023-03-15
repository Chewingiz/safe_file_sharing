import json
import ftplib
import base64
from rsa import rsa_enc, rsa_dec, rsa_sign, rsa_verify, h, gen_rsa_keypair 
from Crypto.Cipher import AES
import os
import ast


from users_gestion import get_key, add_file

def generate_key():
    return os.urandom(16)

#AES

def encrypt(message, key):
    cipher = AES.new(key, AES.MODE_EAX)
    #print(type(message))
    ciphertext, tag = cipher.encrypt_and_digest(message)

    #ciphertext, tag = cipher.encrypt_and_digest(bytes(message))
    return ciphertext, tag

def decrypt(ciphertext, tag, key):
    #cipher = AES.new(key, AES.MODE_EAX, nonce=os.urandom(12))
    cipher = AES.new(key, AES.MODE_EAX, nonce=os.urandom(12))
    #cipher = AES.new(key, AES.MODE_EAX, nonce=cipher.nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext

def send_to(ftp, sender, sender_private_key, receptionist, receptionist_private_key, file_name ):
    """ftp = ftplib.FTP(S_host_n)
    ftp.login(user = S_user_n, passwd = S_psw)"""

    receptionist_public_key = get_key(receptionist)
    #print("Receptionist = " +str(receptionist_private_key))
    sender_public_key = get_key(sender)
    #print("Sender = " + str(sender_private_key))
    #sender_private_key = 0 # get from test_password( local_psw)

   # receptionist_public_key, receptionist_private_key  = gen_rsa_keypair( 1024 )
   # sender_public_key, sender_private_key = gen_rsa_keypair( 1024 )

    key = generate_key()
    print("key = " + str(key))
    """print(type(key))
    print(str(base64.b64encode(key).decode('utf-8')))
    print(str(key))"""
    #enc_key = rsa_enc(str(key), receptionist_public_key)
   #print(len(str(key)))
    #test_str = str(rsa_enc( repr(key), receptionist_public_key))
    #enc_key = int(test_str[slice(0, len(test_str)//2)])
    #print(key)
    enc_key = rsa_enc( repr(key), receptionist_public_key)
    #print(len(str(enc_key)))
    signature = rsa_sign(enc_key, sender_private_key)
    key2 = rsa_dec(enc_key, receptionist_private_key)
    #print(key2)

    with open(file_name, "rb") as file:
        message = file.read()
        #(type(message))
        ciphertext, tag = encrypt(message, key)
        print("tag = " + str(tag))
        with open("key_" + file_name, "w") as file2:
            file2.write("{\n\t\"sender\":\"" + sender  + "\",\n\t\"key\":\"" + str(enc_key)  + "\",\n\t\"signature\":\"" + str(signature) + "\",\n\t\"tag\":\"" + str(base64.b64encode(tag).decode('utf-8')) + "\" \n}")
        with open("enc_" + file_name, "wb") as file3:
            file3.write(ciphertext)
    ftp.cwd("./" + receptionist)

    add_file( ftp, "enc_" + file_name)
    add_file( ftp, "key_" + file_name)

    ftp.cwd("..")
    #test #rsa_verify(signature, sender_public_key)==h(m)

def get_file(ftp, my_private_key, file_name):
    #my_private_key = 0 # get from test_password( local_psw)

    with open("key_" + file_name) as my_file:
        json_key = my_file.read()

    file_info_dict = json.loads(json_key)

    enc_key = int(file_info_dict["key"])
    signature = int(file_info_dict["signature"])
    sender_public_key = get_key(file_info_dict["sender"])
    tag =  base64.b64decode(file_info_dict["tag"])
    print("tag = " + str(tag))
    #print("")
    #print(enc_key)
    #print("")
    
    #print(key)

    if (rsa_verify(signature, sender_public_key) == h(enc_key)):
        print("code autentique")
        #key = bytes.fromhex(rsa_dec(enc_key, my_private_key)[2:-1])
        key = ast.literal_eval(rsa_dec(enc_key, my_private_key))
        print("key = " + str(key))
        with open("enc_" + file_name, "rb") as file:
            enc_message = file.read()
            dec_message = decrypt(enc_message , tag, key)
            with open("dec_" + file_name, "w") as file2:
                file2.write(dec_message.decode())
    else :
        print("message non authentique " )