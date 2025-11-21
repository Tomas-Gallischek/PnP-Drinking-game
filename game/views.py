from django.shortcuts import render
from .models import player


def drink(request):
    player_id = request.GET.get('player_id')
    one_player = player.objects.get(id=player_id)   

    return render(request, 'game/player_info.html', {
        'one_player': one_player})







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