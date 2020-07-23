import smtplib

class EmailNotification:
    def __init__(self, sender_user_name, sender_password, receiver_email):
        self.sender_user_name = sender_user_name
        self.sender_password = sender_password
        self.receiver_email = receiver_email

    def SendEmailNotification(self, subject, body):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        try:
            email_text = "\r\n".join([
                f"From: {self.sender_user_name}",
                f"To: {self.receiver_email}",
                f"Subject: {subject}",
                body
            ])

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.sender_user_name, self.sender_password)
            server.sendmail(self.sender_user_name, self.receiver_email, email_text)
            server.close()

            print(f'Sent email to {self.receiver_email}:')
            print("Subject: " + subject)
            print(body)
        except Exception as e:
            print('Send email failed: ' + e)
