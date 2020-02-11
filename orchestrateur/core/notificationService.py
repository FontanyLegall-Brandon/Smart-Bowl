import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class NotificationService:
    def __init__(self, user_email, pushover_email):
        self.user_email = user_email
        self.pushover_email = pushover_email

        self.smtp_client = smtplib.SMTP(host='mail.hamlab.fr', port=587)
        self.smtp_client.starttls()
        self.smtp_client.login('smart-bowl@hamlab.fr', 'azerty1234%')

    def sendNotification(self, subject, content):
        msg = MIMEMultipart()  # create a message

        # setup the parameters of the message
        msg['From'] = 'smart-bowl@hamlab.fr'
        msg['To'] = self.user_email
        msg['Subject'] = subject

        # add in the message body
        message = content
        msg.attach(MIMEText(message, 'plain'))

        # send the message via the server set up earlier.
        self.smtp_client.send_message(msg)

        msg = MIMEMultipart()  # create a message

        # setup the parameters of the message
        msg['From'] = 'smart-bowl@hamlab.fr'
        msg['To'] = self.pushover_email
        msg['Subject'] = subject

        # add in the message body
        message = content
        msg.attach(MIMEText(message, 'plain'))

        # send the message via the server set up earlier.
        self.smtp_client.send_message(msg)

        del msg