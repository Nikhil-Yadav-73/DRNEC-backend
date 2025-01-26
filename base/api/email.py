from django.core.mail import send_mail

def send_update_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        'nikhilyo2003@gmail.com',
        recipient_list,
    )