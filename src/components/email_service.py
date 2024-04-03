"""Email Service module for sending emails with attachments.

This module provides a class `EmailService` to send emails with attachments.
It reads configuration from a YAML file and fetches environment variables
for sender and recipient details.
"""

import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.utility import get_cfg, get_root


class EmailService:  # pylint: disable=R0903
    """
    Class to send emails with attachments.

    This class reads configuration from a YAML file and fetches environment variables
    for sender and recipient details.

    Attributes:
        config (dict): Configuration dictionary loaded from the YAML file.
        sender_email (str): Email address of the sender (from environment variable).
        sender_password (str): Password of the sender email (from environment variable).
        recipient_email (str): Email address of the recipient (from environment variable).
    """

    def __init__(self):
        """
        Initializes the EmailService object.

        Reads the configuration from the YAML file and retrieves
        sender/recipient details from environment variables.
        """

        self.config = get_cfg("components/email_service.yaml")
        self.sender_email = os.environ.get("EMAIL_SENDER")
        self.sender_password = os.environ.get("EMAIL_PASS")
        self.recipient_email = os.environ.get("EMAIL_RECIPIENT")

    def send_email(self, smtp_server, smtp_port):
        """
        Sends an email with attachments.

        This method composes and sends an email with attachments from a specified folder path.

        Args:
            smtp_server (str): The address of the SMTP server.
            smtp_port (int): The port number of the SMTP server.
        """

        subject = self.config["subject"]

        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = self.recipient_email
        msg["Subject"] = subject

        folder_name = self.config["reports_path"]
        folder_path = os.path.join(get_root(), folder_name)

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as attachment:
                    part = MIMEApplication(attachment.read(), Name=filename)
                part["Content-Disposition"] = f'attachment; filename="{filename}"'
                msg.attach(part)

        text_message = self.config["email_message"]
        msg.attach(MIMEText(text_message, "plain"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(self.sender_email, self.sender_password)
        server.sendmail(self.sender_email, self.recipient_email, msg.as_string())
        server.quit()
