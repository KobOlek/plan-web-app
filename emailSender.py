import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender():
    def __init__(self, email, password):
        self.__email = email
        self.__password = password

    def send_email(self, msg: str, to_email, subject: str):
        body = msg

        message = MIMEMultipart()
        message['From'] = self.__email
        message['To'] = to_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        smtp_session = smtplib.SMTP('smtp-mail.outlook.com', 587)

        smtp_session.starttls()

        smtp_session.login(self.__email, self.__password)

        smtp_session.sendmail(self.__email, to_email, message.as_string())

        smtp_session.quit()
