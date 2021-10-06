from smtplib import SMTP
from ssl import create_default_context
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email_config
from template_email import TEMPLATES


smtp_server = email_config.SMTP_SERVER
port = email_config.PORT

source_email = email_config.SOURCE_EMAIL
v_pass = email_config.V_PASS

target_email = email_config.TARGET_EMAIL
sms_email  =  email_config.SMS_EMAIL

sender_machine  =  email_config.SENDER_MACHINE

templates  =  TEMPLATES


def send_email(msg_subject,
               msg_body,
               debug = False,
               machine = None,
               sms = None):
    
    context = create_default_context()
    server = SMTP(smtp_server, port)
    server.starttls(context = context)

    subject = "{}".format(msg_subject)
    body = "{}".format(msg_body)
    text = MIMEText(body, "plain", "utf-8")
    
    msg = MIMEMultipart()
    msg["From"] = source_email
    msg["Subject"] = "{} / {}".format(subject, sender_machine)

    if sms and machine is not None:
        msg["To"] = sms_email
        msg["CC"] = target_email
        all_targets = [sms_email, target_email]
    else:
        msg["To"] = "{}".format(target_email)
        all_targets = [target_email]

    msg.attach(text)

    full_text = msg.as_string()

    if debug is True:
        server.set_debuglevel(1)
        #DEBUG
        print("\n{}".format(msg.values()))
        print("\n{}".format(msg.keys()))


    server.login(source_email, v_pass)
    server.sendmail(source_email, all_targets, full_text)
    server.quit()

