from django.shortcuts import render, redirect # Přidat 'redirect'
from .models import player, side_quest, side_quest_databese
import random


def quest_done(request):
    if request.method == 'POST':
        user=request.user
        advisor = player.objects.get(id=user.id)
        quest_id = request.POST.get('quest_id')
        completed_quest = side_quest.objects.get(id=quest_id)
        one_player = completed_quest.player
        reward = completed_quest.xp_reward


        one_player.xp += reward
        completed_quest.done = True
        completed_quest.advisor = advisor.name

        completed_quest.save()
        one_player.save()

        return redirect('nastenka')
    
    return redirect('index')

def nastenka(request):
    if request.method == 'POST':
        user=request.POST.get('player_id')
        one_player = player.objects.get(id=user)
        all_quests = side_quest.objects.exclude(player=one_player)


        return render(request, 'game/nastenka.html', context={
            'player_info': one_player,
            'all_quests': all_quests,
        })

    return render(request, 'game/nastenka.html')

def quest_failed(request):
    if request.method == 'POST':
        user=request.POST.get('player_id')
        one_player = player.objects.get(id=user)
        quest_id = request.POST.get('quest_id')
        failed_quest = side_quest.objects.get(id=quest_id, player=one_player)

        failed_quest.delete()

        return redirect('player_info', player_id=one_player.id)
    
    return redirect('index')

def take_quest(request):
    if request.method == 'POST':
        user=request.POST.get('player_id')
        one_player = player.objects.get(id=user)
        quest_id = request.POST.get('quest_id')
        selected_quest = side_quest_databese.objects.get(id=quest_id)
        user_quests = side_quest.objects.filter(player=one_player)

        user_quests.create(
            player=one_player,
            quest_name=selected_quest.quest_name,
            description=selected_quest.description,
            xp_reward=selected_quest.xp_reward,
            rarity=selected_quest.rarity,
            done=False,
        )

        return redirect('player_info', player_id=one_player.id)
    
    return redirect('index')

def sidequest(request):
    if request.method == 'POST':
        user=request.POST.get('player_id')
        one_player = player.objects.get(id=user)

    all_quests = side_quest_databese.objects.all()
    random_quest_1 = random.choice(all_quests)
    random_quest_2 = random.choice(all_quests)
    random_quest_3 = random.choice(all_quests)







    return render(request, 'game/side_quest.html', context={
        'player_info': one_player,
        'random_quest_1': random_quest_1,
        'random_quest_2': random_quest_2,
        'random_quest_3': random_quest_3
    })

def drink(request, player_id):
    one_player = player.objects.get(id=player_id)

    if request.method == 'POST':
        drink_type = request.POST.get('drink_type')
        print(drink_type)
        if drink_type == 'panak':
            one_player.add_xp(50)
            one_player.panak += 1
        elif drink_type == 'maly_kelimek':
            one_player.add_xp(30)
            one_player.maly_kelimek += 1
        elif drink_type == 'velky_kelimek':
            one_player.add_xp(40)
            one_player.velky_kelimek += 1
        one_player.save()

        return redirect('player_info', player_id=one_player.id)
    

    return redirect('player_info', player_id=one_player.id)


def player_info(request, player_id):
    
    one_player = player.objects.get(id=player_id)
    player_quests = side_quest.objects.filter(player=one_player)

    return render(request, 'game/player_info.html', {
        'one_player': one_player,
        'player_quests': player_quests,
        
        })



def leaderboard(request):
    all_players = player.objects.all()
    all_players = all_players.order_by('xp').reverse()

    

    return render(request, 'game/leaderboard.html', {
        'all_players': all_players})

def index(request):
    return render(request, 'game/index.html')