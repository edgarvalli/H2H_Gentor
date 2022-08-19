import os
import time
import paramiko
from datetime import datetime
from helpers.sapws.sapws import SapWS
from helpers.gentormailer import GentorMailer,EmailAttachment
from helpers import db

APIDECODECIFRADO = "C:\\apicifrado\\CmpApiCifradoDecode.bat"
DECRYPT_IN = "C:\\apicifrado\\DecodeEntrada"
DECRYPT_OUT = "C:\\apicifrado\\DecodeSalida"
USER = "089000005643"
HOST = "192.240.110.98"

def insert_to_sap(filepath: str, id: int = 0):
    while os.path.exists(filepath) == False:
        print("El archivo no existe aun")
    
    r = db.fetchone(f"select * from bankfiles where Id={id}")
    mode = r.get("Mode","dev")

    sapws = SapWS()
    sapws.mode = mode
    sapws.render_binary_to_base64(filepath)
    r = sapws.insert_payment_file()

    db.update(f"UPDATE bankfiles SET FileOut='{sapws.binaryB64}' WHERE Id={id}")

    rows = ""

    if mode == "dev":
        mode = "Pruebas"
    else:
        mode = "Producción"

    for row in r.message.split("\n"):
        rows += "<tr><td>" + row + "</td></tr>"

    html = f"""
        <h4>Documento insertado en el SAP de {mode}</h4>
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
    # mailer.emails_recipients.append("vcoronado@gentor.com")
    mailer.subject = "[EVENTLOG][H2H] Archivo guardado"
    mailer.send(html=html)

def decrypt_file(filename=""):
    
    id = filename.split("_")
    filename = id[1]
    id = id[0]

    filein_path = f"{DECRYPT_IN}\\{filename}"
    fileout_path = f"{DECRYPT_OUT}\\{filename.replace('.in','.out')}"
    cmd = f"{APIDECODECIFRADO} {filein_path} {fileout_path}"
    # print(cmd)
    os.system(cmd)
    return {"id": id, "filename": filename}


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

            backup_path = f"{outpath}\\backup\\{file}"
            file_path = f"{outpath}\\{file}"

            sftp.get(file, backup_path)
            sftp.get(file, file_path)


            print("Desencriptando archivo")
            filedata = decrypt_file(file)
            # newfilename = filedata.get("filename","noname")
            id = filedata.get("id",0)

            # os.rename(backup_path, f"{outpath}\\backup\\{newfilename}")
            # os.rename(backup_path, f"{outpath}\\{newfilename}")

            print("Removiendo archivo del servidor")
            sftp.remove(file)
            print(f"Subiendo el archivo al SAP ({fileout_path})")
            insert_to_sap(filepath=fileout_path, id=id)
    
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
