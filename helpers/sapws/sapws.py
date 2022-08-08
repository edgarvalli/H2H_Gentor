import requests

class SapWS:
    endpoint = {
        "dev": "https://my351064.sapbydesign.com/sap/bc/srt/scs/sap/yy95u890ay_ws_insertpaymentfil?sap-vhost=my351064.sapbydesign.com",
        "prod": ""
    }

    mode = "dev"

    def insert_payment_file():
        f = open("payment_file_request.xml","r")
        xml_content = f.read()
        f.close()

        print(xml_content)
        
        return