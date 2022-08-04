import os,time
# from datetime import datetime
from helpers import sftplib

APICIFRADO = "C:\\apicifrado\\CmpApiCifrado.bat"
APIDECODECIFRADO = "C:\\apicifrado\\CmpApiCifradoDecode.bat"
ENCRYPT_IN = "C:\\apicifrado\\CifradoEntrada"
ENCRYPT_OUT = "C:\\apicifrado\\CifradoSalida"
FILE_PATH = "C:\\H2H_SERVER\\output\\sap.txt"
DECRYPT_IN = "C:\\apicifrado\\DecodeEntrada"
DECRYPT_OUT = "C:\\apicifrado\\DecodeSalida"


def encrypt_file(file=FILE_PATH, filename="payment"):
    # filename = f"tran{datetime.now().strftime('%Y%m%d%H%M%S_%f')}.in"

    filename = f"{filename}.in"

    fileout = f"{ENCRYPT_OUT}\\{filename}"

    cmd = f'{APICIFRADO} "{file}" "{fileout}"'
    print(cmd)
    os.system(cmd)

    while os.path.exists(fileout) is False:
        print("Waiting for file")
        time.sleep(1)

    sftp = sftplib.sftp_client()
    sftp.chdir("Inbound")
    sftp.put(localpath=fileout, remotepath=filename)

def decrypt_file(filename=""):
    filein_path = f"{DECRYPT_IN}\\{filename}"
    fileout_path = f"{DECRYPT_OUT}\\{filename}"
    os.system(f"{APIDECODECIFRADO} {filein_path} {fileout_path}")
    # while os.path.exists(fileout_path) is False:
    #     print("Waiting for file")
    #     time.sleep(1)
    # os.system(f"C:\\H2H_SERVER\\scripts\\UploadToSap\\GetFileBankSap.exe {fileout_path}")
