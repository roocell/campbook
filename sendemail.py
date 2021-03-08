import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "asdf@gmail.com"  # Enter your address
receiver_email = "asdf@gmail.com"  # Enter receiver address
password = input("Type your password and press enter: ")

def send(msg):
    message = MIMEMultipart("alternative")
    message["Subject"] = "new cancellation"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = msg
    html = "<html><body><p>new cancellation<br>" + msg + "</p></body></html>"

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
