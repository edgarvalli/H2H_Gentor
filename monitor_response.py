import os
import time
import paramiko
from datetime import datetime
from helpers.sapws.sapws import SapWS
from helpers.gentormailer import GentorMailer,EmailAttachment

APIDECODECIFRADO = "C:\\apicifrado\\CmpApiCifradoDecode.bat"
DECRYPT_IN = "C:\\apicifrado\\DecodeEntrada"
DECRYPT_OUT = "C:\\apicifrado\\DecodeSalida"
USER = "089000005643"
HOST = "192.240.110.98"

def insert_to_sap(filepath: str):
    while os.path.exists(filepath) == False:
        print("El archivo no existe aun")
        
    sapws = SapWS()
    sapws.render_binary_to_base64(filepath)
    r = sapws.insert_payment_file()

    rows = ""

    for row in r.message.split("\n"):
        rows += "<tr><td>" + row + "</td></tr>"

    html = f"""
        <table>
            {rows}
        </table>
    """

    attach = EmailAttachment()
    attach.filename = os.path.basename(filepath)
    f = open(filepath, "rb")
    attach.content = f.read()
    attach.filename = os.path.basename(filepath).replace(".out",".txt")
    f.close()

    mailer = GentorMailer()
    mailer.attachemnts.append(attach)
    mailer.emails_recipients.append("evalli@gentor.com")
    mailer.emails_recipients.append("vcoronado@gentor.com")
    mailer.subject = "[EVENTLOG][H2H] Archivo guardado"
    mailer.send(html=html)

def decrypt_file(filename=""):
    filein_path = f"{DECRYPT_IN}\\{filename}"
    fileout_path = f"{DECRYPT_OUT}\\{filename.replace('.in','.out')}"
    cmd = f"{APIDECODECIFRADO} {filein_path} {fileout_path}"
    # print(cmd)
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
            # output_file = f"{outpath}\\{file}"
            fileout_path = f"{DECRYPT_OUT}\\{file.replace('.in','.out')}"
            
            __log = f"""
                ================================================================================
                =                                                                              =
                =                                                                              =
                =                       {file}                                                 =
                =                                                                              =
                =                                                                              =
                ================================================================================
            """

            print(__log)
            print("Obteniendo archivo del servidor")
            sftp.get(file, f"{outpath}\\backup\\{file}")
            sftp.get(file, f"{outpath}\\{file}")
            print("Desencriptando archivo")
            decrypt_file(file)
            print("Removiendo archivo del servidor")
            sftp.remove(file)
            print(f"Subiendo el archivo al SAP ({fileout_path})")
            insert_to_sap(filepath=fileout_path)
    
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
