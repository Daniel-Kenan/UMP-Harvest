from django.core.mail import send_mail
from django.http import HttpResponse

def send_test_email(request):
    try:
        send_mail(
            'Test Email Subject',
            'This is a test email body.',
            'botauto212@gmail.com',  # Replace with your actual email or DEFAULT_FROM_EMAIL
            ['sdanielkenan@gmail.com'],  # Replace with the recipient's email address
            fail_silently=False,
        )
        return HttpResponse("Test email sent successfully!")
    except Exception as e:
        return HttpResponse(f"Failed to send email: {str(e)}")
