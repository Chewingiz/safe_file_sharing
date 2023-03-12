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

#create new user

def add_new_user( name, public_key):
    ftp = ftplib.FTP(S_host_n)
    ftp.login(user = S_user_n, passwd = S_psw)

    filename = "users.json"

    if filename in ftp.nlst():
        print("Le fichier existe sur le serveur FTP")
        with open(filename, 'rb') as file:
            lines = file.readlines()
            # Supprimer la dernière ligne
            lines.pop()
            lines.pop()
            
            # Ajouter une nouvelle ligne
            new_line = ("\t},\n\t{\n\t\t\"name\" : \"" + name + "\",\n\t\t\"public_key\" : \"" + public_key + "\"\n\t}\n]}").encode('utf-8')
            lines.append(new_line)

            # Écrire le fichier mis à jour localement
            with open(filename, 'wb') as file:
                file.writelines(lines)

            add_file( ftp, filename)

    else:
        with open(filename, "w") as new_file:
            new_file.write("{\n\t\"users\":[{\n\t\t\"name\" : \"" + name + "\",\n\t\t\"public_key\" : \"" + public_key + "\"\n\t}\n]}")

        add_file( ftp, filename)

    ftp.quit()  

add_new_user( "name", "public_key")
#delete_file("users.json")
#add_file( "users.json")