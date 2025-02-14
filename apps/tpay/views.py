from django.shortcuts import render

# Create your views here.


def return_html_accept(nombre):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Solicitud Aprobada</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); text-align: center; }}
            .header {{ background: #4CAF50; padding: 15px; color: white; font-size: 22px; font-weight: bold; border-top-left-radius: 8px; border-top-right-radius: 8px; }}
            .content {{ padding: 20px; font-size: 16px; color: #333; }}
            .button {{ display: inline-block; padding: 12px 25px; background: #4CAF50; color: white; text-decoration: none; font-size: 16px; border-radius: 5px; margin-top: 15px; }}
            .footer {{ margin-top: 20px; font-size: 14px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">¡Solicitud Aprobada! ✅</div>
            <div class="content">
                <p>Estimado/a {nombre},</p>
                <p>Nos complace informarle que su solicitud ha sido aprobada con éxito. 🎉</p>
                <p>Queremos agradecerle por su participación y confianza en nosotros. Estamos emocionados de acompañarlo/a en este proceso.</p>
                <p>Si tiene alguna pregunta, no dude en ponerse en contacto con nuestro equipo.</p>
                <a href="#" class="button">Ver Detalles</a>
                <p class="footer">Atentamente,<br>El equipo de [Nombre de la Empresa]</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


def return_html_rejected(nombre):
    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Solicitud Rechazada</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); text-align: center; }}
                .header {{ background: #d9534f; padding: 15px; color: white; font-size: 22px; font-weight: bold; border-top-left-radius: 8px; border-top-right-radius: 8px; }}
                .content {{ padding: 20px; font-size: 16px; color: #333; }}
                .button {{ display: inline-block; padding: 12px 25px; background: #d9534f; color: white; text-decoration: none; font-size: 16px; border-radius: 5px; margin-top: 15px; }}
                .footer {{ margin-top: 20px; font-size: 14px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">Solicitud No Aprobada ❌</div>
                <div class="content">
                    <p>Estimado/a {nombre},</p>
                    <p>Queremos agradecerle por su interés y participación. Lamentablemente, su solicitud no ha sido aprobada en esta ocasión.</p>
                    <p>Si desea obtener más información o volver a intentarlo en el futuro, no dude en ponerse en contacto con nuestro equipo.</p>
                    <p>¡Gracias por su tiempo y confianza en nosotros!</p>
                    <a href="#" class="button">Más Información</a>
                    <p class="footer">Atentamente,<br>El equipo de [Nombre de la Empresa]</p>
                </div>
            </div>
        </body>
        </html>
        """
    return html_content