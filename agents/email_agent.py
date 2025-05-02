import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class EmailAgent:
    """Agent responsible for sending podcast notifications via email."""
    
    def __init__(self):
        """Initialize the EmailAgent."""
        # Get email configuration from environment variables
        self.sender_email = os.environ.get("EMAIL_SENDER", "")
        self.smtp_server = os.environ.get("SMTP_SERVER", "")
        self.smtp_port = int(os.environ.get("SMTP_PORT", 587))
        self.smtp_username = os.environ.get("SMTP_USERNAME", "")
        self.smtp_password = os.environ.get("SMTP_PASSWORD", "")
    
    def send_notification(self, subscribers, podcast_info, audio_path=None):
        """
        Send podcast notification emails to subscribers.
        
        Args:
            subscribers (list): List of subscriber email addresses.
            podcast_info (dict): Information about the podcast.
            audio_path (str, optional): Path to the podcast audio file.
            
        Returns:
            bool: True if emails were sent successfully, False otherwise.
        """
        if not self.sender_email or not self.smtp_server:
            print("Email configuration missing. Cannot send notifications.")
            return False
        
        if not subscribers:
            print("No subscribers to send notifications to.")
            return False
        
        try:
            # Create email content
            subject = f"New Podcast Episode: {podcast_info['title']}"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #2c3e50; }}
                    .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
                    .cta {{ display: inline-block; background-color: #3498db; color: white; 
                           padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>{podcast_info['title']}</h1>
                    
                    <div class="summary">
                        <p>{podcast_info['summary']}</p>
                    </div>
                    
                    <p>Topics covered in this episode:</p>
                    <ul>
                        {''.join('<li>' + tag.replace('#', '') + '</li>' for tag in podcast_info['hashtags'])}
                    </ul>
                    
                    <p><a href="#" class="cta">Listen Now</a></p>
                    
                    <p>Thanks for subscribing to our podcast!</p>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            New Podcast Episode: {podcast_info['title']}
            
            {podcast_info['summary']}
            
            Topics covered in this episode:
            {', '.join(tag.replace('#', '') for tag in podcast_info['hashtags'])}
            
            Listen now at [Your Podcast Link]
            
            Thanks for subscribing to our podcast!
            """
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            # Send emails to each subscriber
            for subscriber in subscribers:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.sender_email
                msg['To'] = subscriber
                
                # Attach text and HTML versions
                msg.attach(MIMEText(text_content, 'plain'))
                msg.attach(MIMEText(html_content, 'html'))
                
                # Attach audio file if provided
                if audio_path and os.path.exists(audio_path):
                    with open(audio_path, 'rb') as attachment:
                        part = MIMEBase('audio', 'mp3')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{os.path.basename(audio_path)}"'
                    )
                    msg.attach(part)
                
                # Send the email
                server.sendmail(self.sender_email, subscriber, msg.as_string())
            
            # Close the connection
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending email notifications: {e}")
            return False
    
    def send_test_email(self, email_address):
        """
        Send a test email to verify email configuration.
        
        Args:
            email_address (str): Email address to send the test to.
            
        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        if not self.sender_email or not self.smtp_server:
            print("Email configuration missing. Cannot send test email.")
            return False
        
        try:
            # Create email content
            subject = "Test Email from AI Podcast Creator"
            
            html_content = """
            <html>
            <body>
                <h1>Test Email</h1>
                <p>This is a test email from the AI Podcast Creator application.</p>
                <p>If you received this email, your email configuration is working correctly.</p>
            </body>
            </html>
            """
            
            text_content = """
            Test Email from AI Podcast Creator
            
            This is a test email from the AI Podcast Creator application.
            If you received this email, your email configuration is working correctly.
            """
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            # Create and send the email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = email_address
            
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            server.sendmail(self.sender_email, email_address, msg.as_string())
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending test email: {e}")
            return False
