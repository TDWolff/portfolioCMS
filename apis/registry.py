from encrypt_strings import multi_pass_encrypt

def registryUSRLOGIN(usr, pswd):
    if usr == "" or pswd == "":
        return "Username or password cannot be empty."
    encryptedUSR = multi_pass_encrypt(usr)
    encryptedPSWD = multi_pass_encrypt(pswd)
    usrcheckedLine = ""
    pswdcheckedLine = ""
    with open("apis/encrypted_strings.txt", "r") as f:
        usrcheckedLine = f.readline().strip()
        pswdcheckedLine = f.readline().strip()
    if usrcheckedLine == encryptedUSR and pswdcheckedLine == encryptedPSWD:
        print(f"User '{usr}' logged in successfully.")
        return f"Logged in successfully!"
    else:
        return "Invalid username or password."