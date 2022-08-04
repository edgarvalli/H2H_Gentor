import os
import time
import paramiko
from datetime import datetime

APIDECODECIFRADO = "C:\\apicifrado\\CmpApiCifradoDecode.bat"
DECRYPT_IN = "C:\\apicifrado\\DecodeEntrada"
DECRYPT_OUT = "C:\\apicifrado\\DecodeSalida"
USER = "089000005643"
HOST = "192.240.110.98"


def decrypt_file(filename=""):
    filein_path = f"{DECRYPT_IN}\\{filename}"
    fileout_path = f"{DECRYPT_OUT}\\{filename.replace('.in','.out')}"
    cmd = f"{APIDECODECIFRADO} {filein_path} {fileout_path}"
    print(cmd)
    os.system(cmd)


def monitor():

    ciphers = "aes256-cbc"
    pkey = "C:\\Users\\genadmin\\.ssh\\id_rsa"
    pkey = paramiko.RSAKey.from_private_key_file(pkey)

    transport = paramiko.Transport((HOST, 22))
    transport.get_security_options().ciphers = tuple(ciphers.split(","))
    transport.connect(None, USER, pkey=pkey)

    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.chdir("Outbound")

    files = sftp.listdir(".")
    exclude = ["respaldo"]
    outpath = "C:\\apicifrado\\DecodeEntrada"

    for file in files:
        if file not in exclude:
            output_file = f"{outpath}\\{file}"
            fileout_path = f"{DECRYPT_OUT}\\{file.replace('.in','.out')}"
            print(os.path.exists(output_file))
            if os.path.exists(output_file) is False:
                print(fileout_path)
                print("Obteniendo archivo del servidor")
                sftp.get(file, f"{outpath}\\backup\\{file}")
                sftp.get(file, f"{outpath}\\{file}")
                print("Desencriptando archivo")
                decrypt_file(file)
                print("Removiendo archivo del servidor")
                sftp.remove(file)
                print(f"Subiendo el archivo al SAP ({fileout_path})")
                #os.system(f'C:\\H2H_SERVER\\scripts\\UploadToSap\\GetFileBankSap.exe "{fileout_path}"')
    sftp.close()

# monitor()
while True:
    current_minutes = datetime.now().minute

    if current_minutes == 0:
        monitor()
    
    time_to_sleep = (60 - current_minutes) * 60

    print('Monitoring sftp server')
    time_to_sleep = 30
    time.sleep(time_to_sleep)
    monitor()
