from email.message import EmailMessage
import smtplib
import ssl


class MailSender(object):
    def __init__(self, dct_cred):
        self.str_email_sender = dct_cred.get("email_address")
        self.str_email_password = dct_cred.get("password")
        self.em = EmailMessage()

    def mail_configure(self, str_email_receiver, str_subject, str_corpus):
        self.em["From"] = self.str_email_sender
        self.em["To"] = str_email_receiver
        self.em["Subject"] = str_subject
        self.em.set_content(str_corpus)

    def mail_sender(self):

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(self.str_email_sender, self.str_email_password)
            smtp.sendmail(self.str_email_sender, self.em.get("To"), self.em.as_string())


# email_receiver = "dani.testav@gmail.com"
#
# subject = "Email di prova"
# body = """Prova se
#             Funziona la mail"""
#
# em = EmailMessage()
#
# em["From"] = email_sender
# em["To"] = email_receiver
# em["Subject"] = subject
# em.set_content(body)
#
# context = ssl.create_default_context()
#
# with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
#     smtp.login(email_sender, email_password)
#     smtp.sendmail(email_sender, email_receiver, em.as_string())
