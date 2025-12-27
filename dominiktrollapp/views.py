from django.shortcuts import render

def dominik_troll(request):
    return render(request, 'dominiktrollapp/dominiktroll.html')

def vez(request):
    return render(request, 'dominiktrollapp/vez.html')