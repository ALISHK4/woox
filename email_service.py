import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv


def _get_env(name: str, *, required: bool = True    , default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if required and (value is None or str(value).strip() == ""):
        raise RuntimeError(f"Не установлена переменная окружения {name}")
    return value if value is not None else ""


def send_reservation_email(*, name: str, phone: str, guests: str, date: str, destination: str) -> None:
    # Загружаем .env из каталога backend на случай прямого вызова функции
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path=dotenv_path)

    # SMTP_HOST - адрес SMTP сервера, например: smtp.gmail.com
    smtp_host = _get_env("SMTP_HOST")
    # SMTP_PORT - порт SMTP, например: 587 для STARTTLS (рекомендуется)
    smtp_port = int(_get_env("SMTP_PORT"))
    # SMTP_USER - логин/почта отправителя, например: yourmail@gmail.com
    smtp_user = _get_env("SMTP_USER")
    # SMTP_PASSWORD - пароль приложения SMTP (НЕ обычный пароль почты)
    smtp_password = _get_env("SMTP_PASSWORD")
    # TO_EMAIL - адрес, на который будут приходить заявки
    to_email = _get_env("TO_EMAIL")
    # FROM_EMAIL - адрес отправителя (можно не задавать, тогда будет использоваться SMTP_USER)
    from_email = os.environ.get("FROM_EMAIL", smtp_user)
    # SMTP_USE_TLS - использовать ли STARTTLS (true/false). Для порта 587 укажите true
    use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() in {'1', 'true', 'yes'}

    subject = "Новое бронирование"
    body = (
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Гостей: {guests}\n"
        f"Дата: {date}\n"
        f"Направление: {destination}\n"
    )

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain", _charset="utf-8"))

    # Улучшенная логика подключения к SMTP серверу
    server = None
    try:
        if use_tls:
            # Для TLS соединения (порт 587)
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
            server.ehlo()
            server.starttls()
            server.ehlo()
        else:
            # Для SSL соединения (порт 465)
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20)

        # Аутентификация
        server.login(smtp_user, smtp_password)

        # Отправка письма (UTF-8)
        server.sendmail(from_email, [to_email], message.as_string())
        print("Письмо успешно отправлено!")

    except smtplib.SMTPAuthenticationError as err:
        raise RuntimeError("Ошибка аутентификации SMTP: проверьте логин/пароль или пароль приложения") from err
    except smtplib.SMTPConnectError as err:
        raise RuntimeError("Ошибка подключения к SMTP серверу: проверьте хост/порт/доступ в сеть") from err
    except smtplib.SMTPException as err:
        raise RuntimeError(f"SMTP ошибка: {err}") from err
    except Exception as err:
        raise RuntimeError(f"Неизвестная ошибка при отправке письма: {err}") from err
    finally:
        # Всегда закрываем соединение
        try:
            if server is not None:
                server.quit()
        except Exception:
            pass  # Игнорируем ошибки при закрытии соединения