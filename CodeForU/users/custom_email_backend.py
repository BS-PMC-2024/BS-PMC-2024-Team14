import smtplib
from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        print("CustomEmailBackend __init__ method called")
        super().__init__(*args, **kwargs)

    def _starttls(self):
        print("CustomEmailBackend _starttls method called")  # Debugging output
        self.connection.starttls()  # Manually start TLS without keyfile and certfile

    def open(self):
        """Ensure the SMTP connection is open and start TLS if enabled."""
        print("CustomEmailBackend: Opening connection")
        if self.connection:
            print("CustomEmailBackend: Connection already open")
            return False

        # Establish the SMTP connection using just the host and port
        self.connection = smtplib.SMTP(self.host, self.port)
        print("CustomEmailBackend: Connection established")

        if self.use_tls:
            print("CustomEmailBackend: TLS is enabled, starting TLS")
            self.connection.starttls()
            print("CustomEmailBackend: TLS started successfully")

        # Perform the login
        if self.username and self.password:
            self.connection.login(self.username, self.password)
            print("CustomEmailBackend: Logged in successfully")

        return True
