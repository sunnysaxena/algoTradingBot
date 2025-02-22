import smtplib
import telegram
from email.mime.text import MIMEText


class Alerts:
    """
    Handles real-time alerts for the algorithmic trading system.

    Supports notifications via email and Telegram.
    """

    def __init__(self, config):
        """
        Initialize alert system with configuration settings.

        :param config: Dictionary containing email and Telegram settings.
        """
        self.config = config
        self.telegram_bot = telegram.Bot(token=self.config["telegram"]["bot_token"])

    def send_email(self, subject, message):
        """
        Send an email alert.

        :param subject: Subject of the email.
        :param message: Email body content.
        """
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = self.config["email"]["sender"]
        msg['To'] = self.config["email"]["receiver"]

        with smtplib.SMTP(self.config["email"]["smtp_server"], self.config["email"]["smtp_port"]) as server:
            server.starttls()
            server.login(self.config["email"]["sender"], self.config["email"]["password"])
            server.sendmail(self.config["email"]["sender"], self.config["email"]["receiver"], msg.as_string())

    def send_telegram_message(self, message):
        """
        Send a Telegram alert message.

        :param message: The message to send.
        """
        chat_id = self.config["telegram"]["chat_id"]
        self.telegram_bot.send_message(chat_id=chat_id, text=message)
