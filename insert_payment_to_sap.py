import sys,os
from helpers.sapws.sapws import SapWS
from helpers.gentormailer import GentorMailer,EmailAttachment

if len(sys.argv) == 1:
    print("Debe definir la ruta en un argumento")
    sys.exit()


filepath = sys.argv[1]

if os.path.exists(filepath):
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
    f.close()

    mailer = GentorMailer()
    mailer.attachemnts.append(attach)
    mailer.emails_recipients.append("evalli@gentor.com")
    mailer.emails_recipients.append("becario.ti@gentor.com")
    mailer.subject = "[EVENTLOG][H2H] Archivo guardado"
    mailer.send(html=html)



else:
    print(f"{filepath} no es una ruta valida")
    sys.exit()