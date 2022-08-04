import paramiko

def sftp_client():
    USER = "089000005643"
    HOST = "192.240.110.98"

    ciphers = "aes256-cbc"
    pkey = "C:\\Users\\genadmin\\.ssh\\id_rsa"
    pkey = paramiko.RSAKey.from_private_key_file(pkey)

    transport = paramiko.Transport((HOST,22))
    transport.get_security_options().ciphers = tuple(ciphers.split(","))
    transport.connect(None,USER,pkey=pkey)

    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp