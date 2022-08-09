import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart

class EmailAttachment:
    content: bytes
    filename: str

class GentorMailer:
    port = 587

    password = 'Tab60859'
    smtp_server = "smtp.office365.com"
    port = 587  # For starttls
    sender_email = "soporte@gentor.com"
    subject: str = "[EVENTLOG]"

    emails_recipients: list = []
    attachemnts: list[EmailAttachment] = []

    def send(self, html):
        # Try to log in to server and send email
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP(self.smtp_server, self.port)
            server.ehlo()  # Can be omitted
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Can be omitted
            server.login(self.sender_email, self.password)

            msg = MIMEMultipart()
            msg['Subject'] = self.subject
            msg['From'] = self.sender_email
            msg['To'] = ", ".join(self.emails_recipients)

            msg.attach(MIMEText(html,'html'))

            if len(self.attachemnts) > 0: # are there attachments?
                for attach in self.attachemnts:
                    part = MIMEBase('application', "octet-stream")
                    part.set_payload( attach.content )
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment; filename="%s"' % attach.filename)
                    msg.attach(part)

            server.sendmail(self.sender_email,  self.emails_recipients,msg.as_string())
            return "ok"
            # TODO: Send email here
        except Exception as e:
            # Print any error messages to stdout
            print(e)
            return ";".join(e.args)
        finally:
            server.quit()