from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from ..core.config import settings

class SendGridService:
    def __init__(self):
        self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        self.from_email = settings.SENDGRID_FROM_EMAIL

    def send_email(self, to_email: str, subject: str, content: str) -> bool:
        """
        Send an email using SendGrid
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            content: Email content (HTML)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", content)
            )
            
            response = self.sg.send(message)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

# Create a singleton instance
sendgrid_service = SendGridService() 