from django.core.mail import send_mail


def send_mail_function(user, confirmation_code):
    """Отправляет письмо с кодом подтверждения"""
    return send_mail(
        "регистрация на портале YaMDb",
        f"Уважаемый {user}, ваш код подтверждения: {confirmation_code}",
        "yamdb@yamdb.com",
        [user.email],
        fail_silently=False)
