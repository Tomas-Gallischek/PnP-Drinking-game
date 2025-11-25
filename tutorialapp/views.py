from django.shortcuts import render
from game.models import player


def tut_end(request):

    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        povolani = request.POST.get('povolani')
        print(player_id, povolani)
        chosen_player = player.objects.get(id=player_id)
        chosen_player.povolani = povolani
        chosen_player.save()

    return render(request, 'tutorialapp/end_tutorial.html', context={
        "chosen_player": chosen_player,
        })

def vyber_povolani(request):

    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        
        chosen_player = player.objects.get(id=player_id)

    return render(request, 'tutorialapp/vyber_povolani.html', context={
        "chosen_player": chosen_player

    })


def vyber_postavy(request):

    all_players = player.objects.all()
    

    return render(request, 'tutorialapp/vyber_postavy.html', context={
        "all_players": all_players
    })

def tut_seznameni(request):



    return render(request, 'tutorialapp/tut_seznameni.html', context={

    })

def tut_odloz_si(request):

        
    return render(request, 'tutorialapp/tut_odloz_si.html', context={

    })

def tut_zazvonit(request):


    return render(request, 'tutorialapp/tut_zazvonit.html', context={
    })


def welcome(request):


    return render(request, 'tutorialapp/welcome.html', context={
        
        })