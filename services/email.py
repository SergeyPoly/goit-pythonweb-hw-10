from email.mime.text import MIMEText
import smtplib
from conf.config import settings
from auth import create_email_token


async def send_email(email: str, username: str, host: str):
    try:
        token_verification = create_email_token({"sub": email})
        link = f"{host}/api/auth/confirmed_email/{token_verification}"

        message = f"""
        <html>
        <body>
            <h3>Привет, {username}!</h3>
            <p>Для завершения регистрации перейдите по ссылке:</p>
            <p><a href="{link}">Подтвердить email</a></p>
            <p>Спасибо!</p>
        </body>
        </html>
        """

        msg = MIMEText(message, "html")
        msg["Subject"] = "Підтвердження реєстрації"
        msg["From"] = settings.mail_from
        msg["To"] = email

        with smtplib.SMTP(settings.mail_server, settings.mail_port) as server:
            server.starttls()
            server.login(settings.mail_username, settings.mail_password)
            server.sendmail(settings.mail_from, email, msg.as_string())

    except Exception as e:
        print(f"Помилка відправки email: {e}")
