from django.shortcuts import render, redirect # Přidat 'redirect'
from .models import player


def drink(request, player_id):
    one_player = player.objects.get(id=player_id)

    if request.method == 'POST':
        drink_type = request.POST.get('drink_type')
        print(drink_type)
        if drink_type == 'panak':
            one_player.xp += 30
            one_player.panak += 1
        elif drink_type == 'maly_kelimek':
            one_player.xp += 10
            one_player.maly_kelimek += 1
        elif drink_type == 'velky_kelimek':
            one_player.xp += 20
            one_player.velky_kelimek += 1
        one_player.save()

        return redirect('player_info', player_id=one_player.id)
    

    return redirect('player_info', player_id=one_player.id)


def player_info(request, player_id):
    
    one_player = player.objects.get(id=player_id)

    return render(request, 'game/player_info.html', {
        'one_player': one_player})



def leaderboard(request):
    all_players = player.objects.all()
    all_players = all_players.order_by('xp').reverse()

    

    return render(request, 'game/leaderboard.html', {
        'all_players': all_players})

def index(request):
    return render(request, 'game/index.html')