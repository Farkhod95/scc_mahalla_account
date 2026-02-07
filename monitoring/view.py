from django.shortcuts import render


def index(request):
    return render(request, 'gps_index.html', context=dict(text='Hello world'))