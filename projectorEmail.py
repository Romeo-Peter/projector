import imaplib
import email
from email.parser import BytesParser, Parser
from email.policy import default
from datetime import datetime
import re

from decouple import config

time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")


class ReadEmail:
    """Projector email reader"""

    def __init__(self, user, password, provider="imap.gmail.com"):
        self.user = user
        self.password = password
        self.mail = imaplib.IMAP4_SSL(provider)
        self.mail.login(user, password)

        print(f"[{time}] Connecting to mailbox via IMAP")

        mailbox = self.mail.select(mailbox="inbox", readonly=True)

        if mailbox:
            print(f"[{time}] Inbox selected\n")

    def __retrieve_email__(self):
        # Read all mail uids and retrieve latest email
        # Private class method
        __result, __data = self.mail.uid("search", None, "ALL")
        __latest_email_uid = __data[0].split()[-1]
        __result, __data = self.mail.uid("fetch", __latest_email_uid, "(RFC822)")
        __raw_email_data = __data[0][1]

        # Parse email to python object
        return BytesParser(policy=default).parsebytes(__raw_email_data)

    def read_email(self):
        # Retrieve text payload
        email_message = self.__retrieve_email__()

        email_subject = email_message["subject"]
        sender_name_and_email = email.utils.parseaddr(email_message["from"])
        recipient_email = email_message["to"]
        date_sent = email_message["date"]

        email_type = email_message.get_content_maintype()

        if email_type == "multipart":
            for part in email_message.get_payload():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload()
        elif email_type == "text":
            payload = email_message.get_payload()

        f"""
        [SUBJECT]: {email_subject}\b
        [FROM]: <{sender_name_and_email[1]}>\b
        [TO]: {recipient_email}\b
        [DATA]: {date_sent}\n

        [BODY]:\b
        {payload}
        """

        if email_subject == "[GitHub] Please verify your device":
            # Get verification code
            verification_code = re.search("(\d+)", payload)
            print(f"[{time}] verification code copied to clipboard")
            return verification_code.group(0)
