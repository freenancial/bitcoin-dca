import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText

class EmailNotification:
    def __init__(self, sender_user_name, sender_password, receiver_email):
        self.sender_user_name = sender_user_name
        self.sender_password = sender_password
        self.receiver_email = receiver_email

    def sendEmailNotification(self, unwithdrawn_buy_orders):
        subject = datetime.now().strftime("%Y-%m-%d") + " Bitcoin DCA summary",
        body = self.generateDCASummary(unwithdrawn_buy_orders)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        try:
            email_text = "\r\n".join([
                f"From: {self.sender_user_name}",
                f"To: {self.receiver_email}",
                f"Subject: {subject}",
                "",
                body
            ])

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.sender_user_name, self.sender_password)
            
            server.sendmail(self.sender_user_name, self.receiver_email, MIMEText(email_text, "plain"))
            server.close()

            print(f'Sent email to {self.receiver_email}:')
            print("Subject: " + subject)
            print(body)
        except Exception as e:
            print('Send email failed: ' + e)

    def generateDCASummary(self, unwithdrawn_buy_orders):
        summary = ""
        total_cost, total_size = 0, 0
        for order in unwithdrawn_buy_orders:
            order_datetime, cost, size = order
            utc_datetime = datetime.strptime(order_datetime, '%Y-%m-%dT%H:%M:%S.%fZ')
            local_datetime = utc_datetime.replace(tzinfo=timezone.utc).astimezone(tz=None)
            summary += f"{local_datetime.strftime('%Y-%m-%d %H:%M:%S')}, ${round(cost, 2)}, ₿{size}, ${round( cost / size, 2 )}\n"
            total_cost += cost
            total_size += size
        return f"Average Price: {round( total_cost / total_size, 2 )}\n\n" + summary 