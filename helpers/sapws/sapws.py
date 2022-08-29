import requests, os, base64, re, xmltodict
from requests.auth import HTTPBasicAuth
from pathlib import Path

class SapWSResponse:
    error: bool = False
    message: str = ""
    log: tuple = ()
    code: int = 0
    xmltext:str = ""

class SapWS:
    endpoint = {
        "dev": "https://my351064.sapbydesign.com/sap/bc/srt/scs/sap/yy95u890ay_ws_insertpaymentfil?sap-vhost=my351064.sapbydesign.com",
        "prod": "https://my353505.sapbydesign.com/sap/bc/srt/scs/sap/yy95u890ay_ws_insertpaymentfil?sap-vhost=my353505.sapbydesign.com"
    }

    mode = "dev"
    uuid = ""
    binaryB64: bytes = ""

    def render_binary_to_base64(self, filepath: str = ""):
        f = open(filepath,"rb")
        self.binaryB64 = base64.b64encode(f.read())
        self.uuid = Path(filepath).name.split(".")[0]
        f.close()

    def insert_payment_file(self):
        filename = os.path.join(Path(__file__).parent, "payment_file_request.xml")
        f = open(filename,"r")
        xml_content = f.read()
        f.close()

        xml_content = xml_content.replace("{{UUID}}", self.uuid)
        xml_content = xml_content.replace("{{BinaryObject}}", self.binaryB64.decode("utf-8") )
        
        sap_auth = HTTPBasicAuth("SAP_ADMIN","tt3&GQZG6yGI")
        uri = self.endpoint[self.mode]
        headers = {"Content-Type": "text/xml; charset=utf-8"}

        response = requests.post(uri, data=xml_content,headers=headers,auth=sap_auth)
        r = SapWSResponse()
        
        r.xmltext = response.text
        r.code = response.status_code

        if response.status_code == 200:
            
            response_dict = xmltodict.parse(r.xmltext)
            logs = response_dict["soap-env:Envelope"]["soap-env:Body"]
            logs = logs["n0:ZBO_GetDocumentFilePaymentFile_ViewCreateConfirmation_sync"]
            logs = logs["Log"]["Item"]

            for log in logs:
                r.message += log["Note"] +"\n"

        else:
            r.error = True
            r.message = re.findall(r"<h1>(.*?)</h1>", response.text)[0]
            r.message += " | " + response.reason
            
        return r