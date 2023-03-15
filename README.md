# safe_file_sharing
Python app to share files.

# Principle

Every file is encoded with a different randomly generated key that is shared using the RSA protocol between users. The clear file is never shared and can never be found on the server.

# How does it work?

It is kind of complicated; here is an explanation.

Different keys I used:
- User password: chosen by the user.
- RSA key: randomly generated RSA keys created by `gen_rsa_keypair(size)` in `rsa.py`.
- AES key: random 16-byte key.

The file is encoded with AES in GCM mode. To share the key safely, it is encoded with the RSA protocol. To keep the user's RSA private key locally, it is encoded with Fernet. To retrieve the key, the user has to decode it with their user password (the key is a hash of their password).

# How to use it?

## Set server
Create a file named "server_info.json" with the following contents:
```json
{
"host_name": "Hostname",
"port": "Port",
"username": "Username",
"password": "Password"
}
```
Where:  
       - Hostname: Hostname or IP.  
       - Port: Port.  
       - Username: Username.  
       - Password: Password.  

## Functions
There is no GUI yet, so here is an explanation of the main functions:

```py
add_new_user(ftp, *string :* Name, *string :* User_password)													# Add new user.
test_password(*string :* Name, *string :* User_password)														# Returns the private key if the password is valid.
send_to(ftp, *string :* sender, *integer :* sender_private_key, *string :* receptionist, *string :* file_name) 	# Sends a file from the sender to the receptionist.
get_file(ftp, *string :* name, *integer :* my_private_key, *string :* file_name)								# Uploads distant files and decrypts them.

