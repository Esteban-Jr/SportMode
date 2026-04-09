from django.shortcuts import render


def index(request):
    return render(request, 'home/index.html')


def about(request):
    return render(request, 'home/about.html')


def delivery(request):
    return render(request, 'home/delivery.html')


def contact(request):
    return render(request, 'home/contact.html')
