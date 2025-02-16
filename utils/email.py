from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_html_mail(to_email, name, folio, estatus):
    # First, render the plain text content.
    text_content = render_to_string("emails/standar_email_validation.txt", context={"username": name, 'folio': folio, 'estatus': estatus},)

    # Secondly, render the HTML content.
    html_content = render_to_string("emails/standar_email_validation.html", context={"username": name, 'folio': folio, 'estatus': estatus},)

    try:
        # Then, create a multipart email instance.
        msg = EmailMultiAlternatives(
            "Notificación Feria Tabasco 2025",
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [to_email]
        )

        # Lastly, attach the HTML content to the email instance and send.
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        print(e)