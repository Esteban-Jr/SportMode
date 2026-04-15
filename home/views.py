from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings


def index(request):
    return render(request, 'home/index.html')


def about(request):
    return render(request, 'home/about.html')


def delivery(request):
    return render(request, 'home/delivery.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and subject and message:
            send_mail(
                subject=f'[SportsMode Contact] {subject} from {name}',
                message=f'From: {name} <{email}>\n\n{message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            messages.success(
                request,
                "Thanks for your message! We'll get back to you within 1–2 working days."
            )
        else:
            messages.error(request, 'Please fill in all fields before sending.')

        return redirect('contact')

    return render(request, 'home/contact.html')
