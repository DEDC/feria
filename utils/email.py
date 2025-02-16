from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_html_mail():
    # First, render the plain text content.
    text_content = render_to_string("emails/validated_email.txt", context={"my_variable": 42},)

    # Secondly, render the HTML content.
    html_content = render_to_string("emails/validated_email.html", context={"my_variable": 42},)

    # Then, create a multipart email instance.
    msg = EmailMultiAlternatives(
        "Notificación Feria Tabasco 2025",
        text_content,
        "feria@tabasco.gob.mx",
        ["dedc_011596@hotmail.com"],
        headers={"List-Unsubscribe": "<mailto:feria@tabasco.gob.mx>"},
    )

    # Lastly, attach the HTML content to the email instance and send.
    msg.attach_alternative(html_content, "text/html")
    msg.send()