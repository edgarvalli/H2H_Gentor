import os
import base64
import shutil
from helpers import db, jwt
from scripts import h2h_encryptor
from flask import Flask, request, send_file
from functools import wraps

app = Flask(__name__)

UPLOAD_FOLDER = 'h2h'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db.DB_PATH = os.path.join(app.root_path, db.DB_PATH)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class SingInResponse:
    error:bool = False
    message: str = ""
    data: dict = {}

def sing_in(username:str, password: str) -> SingInResponse:
    sql = f"select * from users where email='{username}' and password='{password}'"
    result = db.fetchone(sql)
    response = SingInResponse()
    if result is None:
        response.error = True
        response.message = "Usuario no existe"
    else:
        response.error = False
        response.message = "ok"
        response.data = result

    return response


def auth(f):
    @wraps(f)
    def func(*args, **kvargs):
        if "Token" in request.headers:
            token = request.headers['Token']
            result = jwt.decode(token)

            if result.get('error', True):
                return result

            return f(*args, **kvargs)
        
        elif request.authorization is not None:
            username = request.authorization.get("username")
            password = request.authorization.get("password")
            result = sing_in(username, password)
            if result.error:
                return {
                    "error": True,
                    "message": result.message
                }
            else:
                return f(*args, **kvargs)
        

        else:
            return {
                "error": True,
                "message": "Token no incluido"
            }

    return func


@app.route('/h2h', methods=['GET', 'POST'])
def Index():
    return "H2H Running"


@app.route('/h2h/auth/singin', methods=['POST'])
def auth_singin():

    body = request.get_json()
    email = body.get('email', '')
    password = body.get('password', '')

    # sql = f"select * from users where email='{email}' and password='{password}'"
    # result = db.fetchone(sql)

    result = sing_in(email, password)

    print(result.error)
    if result.error:
        return {
            'error': True,
            'message': 'Usuario o Password son incorrectos'
        }

    return {
        'error': False,
        'token': jwt.encode(result.data)
    }


@app.route('/h2h/portal')
def portal():
    print(request.headers.get("Domain", None))
    return send_file('upload_portal.html')

@app.route('/h2h/wsdl')
def wsdl():
    filename = request.args.get('filename','GetBankDocument_V1')
    return send_file(f'wsdl/{filename}.wsdl')

@app.route('/h2h/upload', methods=['POST'])
@auth
def h2h_request():
    data = request.get_json()
    filename = data.get('fileName', 'sap_layout')
    # filename = filename.replace(" ","_")
    # WINDOWS_LINE_ENDING = b'\r\n'
    # UNIX_LINE_ENDING = b'\n'

    file_content = base64.b64decode(data.get('fileContent', 'empty'))

    file_content = file_content.decode('utf-8').split('\n')
    filename = f"{filename}.{data.get('fileExt','txt')}"
    output_path = f"C:\\H2H_SERVER\\repository\\sap\\{filename}"

    if os.path.exists(output_path):
        os.unlink(output_path)

    # islast = False

    oFile = open(output_path,'a')
    for row in file_content:
        if row.startswith(" ") is False:
            if len(row) > 500:
                r = row[:981]
            else:
                r = row[:481]

            oFile.write(f"{r}\n")
            # os.system(f'echo "{r}" >> {output_path}')
    
    oFile.close()
    cmd = f"powershell C:\\H2H_SERVER\\scripts\\Remove-LastITemTxt.ps1 -Path {output_path}"
    os.system(cmd)

    file_path = f"C:\\H2H_SERVER\\output\\{filename}"
    shutil.copyfile(output_path, file_path)

    h2h_encryptor.encrypt_file(file=file_path, filename=data.get('fileName', 'sap_layout'))

    return {
        "error": False,
        "status": "success"
    }


app.run(port=5000, host='0.0.0.0')
