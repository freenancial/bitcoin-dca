import smtplib
from datetime import datetime

from db_manager import DBManager
from logger import Logger


class EmailNotification:
    def __init__(self, sender_user_name, sender_password, receiver_email):
        self.sender_user_name = sender_user_name
        self.sender_password = sender_password
        self.receiver_email = receiver_email

    def sendEmailNotification(self, unwithdrawn_buy_orders):
        subject = datetime.now().strftime("%Y-%m-%d") + " Bitcoin DCA summary"
        body = EmailNotification.generateDCASummary(unwithdrawn_buy_orders)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        try:
            email_text = "\r\n".join(
                [
                    f"From: {self.sender_user_name}",
                    f"To: {self.receiver_email}",
                    f"Subject: {subject}",
                    "",
                    body,
                ]
            )

            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.ehlo()
            server.login(self.sender_user_name, self.sender_password)
            server.sendmail(self.sender_user_name, self.receiver_email, email_text)
            server.close()

            Logger.info(f"Sent email to {self.receiver_email}:")
            Logger.info(f"Subject: {subject}")
            Logger.info(body)
        except Exception as error:  # pylint: disable=broad-except
            Logger.error("Unable to send email")
            Logger.error(f"error: {error}")

    @staticmethod
    def generateDCASummary(unwithdrawn_buy_orders):
        summary = ""
        total_cost, total_size = 0, 0
        for order in unwithdrawn_buy_orders:
            order_datetime, cost, size = order
            local_datetime = DBManager.convertOrderDatetime(order_datetime)
            summary += (
                f"{local_datetime.strftime('%m-%d %H:%M')}, ${round(cost, 2)}, "
                f"{size}, ${round( cost / size, 0 )}\n"
            )
            total_cost += cost
            total_size += size
        return (
            "Average Price: ${:.2f}\n".format(total_cost / total_size)
            + "Total Cost: ${:.2f}\n".format(total_cost)
            + "Total Size: {:.8f}\n\n".format(total_size)
            + summary
        )
