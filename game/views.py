from hmac import new
from math import e
from multiprocessing import context
from os import error
import profile
import re
import stat
from django.shortcuts import render, redirect
from django.db.models import Q
from fightapp.models import boss, boss_names_descriptions, FightLog, TurnLog
from .models import player, side_quest, side_quest_databese, achievements, jmena_hracu, pocet_hracu, side_quest_generated, test_model
from django.http import HttpResponse
import random
from fightapp.views import fight
import datetime
from django.utils import timezone


def stat_up(request, player_id):
    if request.method == 'POST':
        one_player = player.objects.get(id=player_id)
        stat_type = request.POST.get('stat_type')
        if one_player.skill_points <= 0:
            return redirect('player_info', player_id=player_id)
        else:
            if stat_type == 'dmg':
                random_dmg = random.uniform(0.8, 1.2)
                one_player.dmg_now += round(one_player.dmg_koef * random_dmg)
                one_player.skill_points -= 1
                one_player.save()
            elif stat_type == 'armor':
                random_armor = random.uniform(0.8, 1.2)
                one_player.armor_now += round(one_player.armor_koef * random_armor)
                one_player.skill_points -= 1
                one_player.save()

            elif stat_type == 'hp':
                random_hp = random.uniform(0.8, 1.2)
                one_player.hp_now += round(one_player.hp_koef * random_hp)
                one_player.hp_actual_fight += round(one_player.hp_koef * random_hp)
                one_player.skill_points -= 1
                one_player.save()

            return redirect('player_info', player_id=player_id)

def quest_done(request):
    if request.method == 'POST':
        user=request.user
        quest_id = request.POST.get('quest_id')
        completed_quest = side_quest.objects.get(id=quest_id)
        main_player = completed_quest.player
        coop_player = completed_quest.player_coop or None
        reward = completed_quest.xp_reward

        if coop_player:
            coop_player_instance = player.objects.get(name=coop_player)
            player.add_xp(coop_player_instance, reward)
            coop_player_instance.save()
        player.add_xp(main_player, reward)
        completed_quest.done = True


        completed_quest.save()
        main_player.save()

    return redirect('leaderboard')

def nastenka(request):
    if request.method == 'POST':
        user=request.POST.get('player_id')
        one_player = player.objects.get(id=user)
        all_quests = side_quest.objects.exclude(Q(player=one_player) | Q(player_coop=one_player.name))


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
        failed_quest = side_quest.objects.get(id=quest_id)
        coop_player = failed_quest.player_coop or None
        failed_quest.delete()
        print(f"coop_player: {coop_player}")
        print(f"one_player: {one_player}")
        print(f"failed_quest: {failed_quest}")


        return redirect('player_info', player_id=one_player.id)
    
    return redirect('index')

def take_quest(request):
    if request.method == 'POST':
        user=request.POST.get('player_id') or None
        user_coop = request.POST.get('coop_player_id') or None
        one_player = player.objects.get(id=user)
        coop_player = player.objects.get(id=user_coop) if user_coop else None 
        print(f"Quest pro hráče: {user}, coop hráč: {user_coop}")

        quest_id = request.POST.get('quest_id')
        selected_quest = side_quest_generated.objects.get(id=quest_id)

        one_player.quest_refresh += 1
        one_player.save()

        new_quest = side_quest.objects.create(
            player=one_player,
            player_name= one_player.name,
            player_coop= coop_player.name if coop_player else "",
            coop_player_name= coop_player.name if coop_player else "",
            quest_type=selected_quest.quest_type,
            quest_name=selected_quest.quest_name,
            description=selected_quest.description,
            xp_reward=selected_quest.xp_reward,
            rarity=selected_quest.rarity,
            done=False,
        )       

        new_quest.save()

        one_player.energie -= 20
        one_player.save()
        player.energy_change(one_player)

        print(f"Hráči bylo odečteno 20 energie. Aktuální energie hráče {one_player.name}: {one_player.energie}")

        if coop_player:
            coop_player.energie -= 20
            coop_player.save()
            coop_player.energy_change()
            print(f"Hráči bylo odečteno 20 energie. Aktuální energie hráče {coop_player.name}: {coop_player.energie}" if coop_player else "Žádný coop hráč.")

        expirated_quests = side_quest_generated.objects.filter(player=one_player)
        expirated_quests.delete()

        return redirect('player_info', player_id=one_player.id)
    
    return redirect('index')

def quest_generator(request, player_id):
    one_player = player.objects.get(id=player_id)
    one_player.quest_refresh -= 1
    one_player.save()
    all_quests_alko = side_quest_databese.objects.filter(quest_type='alko')
    all_quests_nealko = side_quest_databese.objects.filter(quest_type='nealko')
    all_quests_coop = side_quest_databese.objects.filter(quest_type='coop')

    random_quest_alko = random.choice(all_quests_alko)
    random_quest_nealko = random.choice(all_quests_nealko)
    random_quest_coop  = random.choice(all_quests_coop)

    new_generated_quest = [random_quest_alko, random_quest_nealko, random_quest_coop]

    for quest in new_generated_quest:
        rarity_roll = random.randint(1, one_player.lvl + 10) #+10 kvůli +1. levelu hrače
        
        if rarity_roll >= 20:
            rarity = 'legendary'
            rarity_kof = 2
        elif rarity_roll >= 16:
            rarity = 'epic'
            rarity_kof = 1.8
        elif rarity_roll >= 12:
            rarity = 'rare'
            rarity_kof = 1.6
        elif rarity_roll >= 8:
            rarity = 'uncommon'
            rarity_kof = 1.4
        elif rarity_roll >= 4:
            rarity = 'common'
            rarity_kof = 1.2
        else:
            rarity = 'common'
            rarity_kof = 1

        xp_reward = (30 + (one_player.lvl * 5)) * rarity_kof

        side_quest_generated.objects.create(
            player=one_player,
            quest_name = quest.quest_name,
            quest_type = quest.quest_type,
            description = quest.description,
            xp_reward = xp_reward,
            rarity = rarity,
        )

def sidequest(request):
    if request.method == 'POST':
        user=request.POST.get('player_id')
        one_player = player.objects.get(id=user)

        player_refresh_points = one_player.quest_refresh
        print(f"Počet refresh pointů hráče {one_player.name}: {player_refresh_points}")
        if player_refresh_points >= 1:
            one_player.save()
            quest_generator(request, one_player.id)


        active_players = player.objects.filter(active=True)

        ready_random_quest_alko = side_quest_generated.objects.filter(player=one_player, quest_type='alko').last()
        ready_random_quest_nealko = side_quest_generated.objects.filter(player=one_player, quest_type='nealko').last()
        ready_random_quest_coop = side_quest_generated.objects.filter(player=one_player, quest_type='coop').last()


        return render(request, 'game/side_quest.html', context={
            'player_info': one_player,
            'random_quest_alko': ready_random_quest_alko,
            'random_quest_nealko': ready_random_quest_nealko,
            'random_quest_coop': ready_random_quest_coop,
            'active_players': active_players,
        })
    

def quest_refresh(request):
    if request.method == 'POST':
        user=request.POST.get('player_id')
        one_player = player.objects.get(id=user)

        if one_player.energie >= 20:
            one_player.energie -= 20
            one_player.quest_refresh += 1
            print("HRÁČI BYLY PŘIČTENY REFRESH POINTY")
            one_player.save()
            side_quest_generated.objects.filter(player=one_player).delete()
            print(f"Hráči bylo odečteno 20 energie za obnovení úkolů. Aktuální energie hráče {one_player.name}: {one_player.energie}")
            quest_generator(request, one_player.id)
            print(f"Hráči {one_player.name} byly obnoveny úkoly.")

        active_players = player.objects.filter(active=True)

        ready_random_quest_alko = side_quest_generated.objects.filter(player=one_player, quest_type='alko').last()
        ready_random_quest_nealko = side_quest_generated.objects.filter(player=one_player, quest_type='nealko').last()
        ready_random_quest_coop = side_quest_generated.objects.filter(player=one_player, quest_type='coop').last()

        return render(request, 'game/side_quest.html', context={
            'player_info': one_player,
            'random_quest_alko': ready_random_quest_alko,
            'random_quest_nealko': ready_random_quest_nealko,
            'random_quest_coop': ready_random_quest_coop,
            'active_players': active_players,
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
    one_player_name = one_player.name

    dmg_koef_min = round(one_player.dmg_koef * 0.8, 1)
    dmg_koef_max = round(one_player.dmg_koef * 1.2, 1)
    armor_koef_min = round(one_player.armor_koef * 0.8, 1)
    armor_koef_max = round(one_player.armor_koef * 1.2, 1)
    hp_koef_min = round(one_player.hp_koef * 0.8, 1)
    hp_koef_max = round(one_player.hp_koef * 1.2, 1)


    one_player.energy_change()
    energy = one_player.energie



    player_quests = side_quest.objects.filter(
        Q(player=one_player) | Q(player_coop=one_player_name), 
        done=False
    )

    print({player_quests})
 

    return render(request, 'game/player_info.html', {
        'one_player': one_player,
        'player_quests': player_quests,
        'dmg_koef_min': dmg_koef_min,
        'dmg_koef_max': dmg_koef_max,
        'armor_koef_min': armor_koef_min,
        'armor_koef_max': armor_koef_max,
        'hp_koef_min': hp_koef_min,
        'hp_koef_max': hp_koef_max,
        'energy': energy,
        
        })



def leaderboard(request):
    all_players = player.objects.all().filter(active=True)
    all_achivements = achievements.objects.all().filter(player__active=True)

    total_dmg_delt = all_achivements.order_by('total_dmg_delt').reverse()
    total_dmg_taken = all_achivements.order_by('total_dmg_taken').reverse()
    death_counter = all_achivements.order_by('death_counter')
    best_dmg = all_achivements.order_by('best_dmg_delt').reverse()


    total_score = all_players.order_by('score').reverse()
    score_dmg_delt = all_players.order_by('score_dmg_delt').reverse()
    score_dmg_taken = all_players.order_by('score_dmg_taken').reverse()
    score_death_counter = all_players.order_by('score_death_counter').reverse()
    score_best_dmg = all_players.order_by('score_best_dmg').reverse()



    return render(request, 'game/leaderboard.html', {
        'all_players': all_players,
        'total_score': total_score,
        'score_dmg_delt': score_dmg_delt,
        'score_dmg_taken': score_dmg_taken,
        'score_death_counter': score_death_counter,
        'score_best_dmg': score_best_dmg,
        'total_dmg_delt': total_dmg_delt,
        'total_dmg_taken': total_dmg_taken,
        'death_counter': death_counter,
        'best_dmg': best_dmg,
        })

def index(request):
    return render(request, 'game/index.html')


def reset(request):
    if request.method == 'POST':
        test_start = test_model.objects.first()
        test_question = test_start.test_status
        

        print(f"Test question value: {test_question}")
        player.objects.all().delete()
        achievements.objects.all().delete()
        boss.objects.all().delete()

        players_default = jmena_hracu.objects.all()



        for i in players_default:
            moznosti_povolani = ['mag', 'valecnik', 'hunter']
            povolani = random.choice(moznosti_povolani)
            if povolani == 'mag':
                dmg = 18
                # dmg_koef = 9 (původní hodnota)
                dmg_koef = 25
                obrana = 2
                obrana_koef = 1.5
                hp = 70
                hp_koef = 50
                role_id = 1
            elif povolani == 'valecnik': 
                dmg = 12
                # dmg_koef = 4
                dmg_koef = 10
                obrana = 10
                obrana_koef = 3
                hp = 120
                hp_koef = 150
                role_id = 3
            elif povolani == 'hunter':
                dmg = 14
                # dmg_koef = 6
                dmg_koef = 15
                obrana = 6
                obrana_koef = 2.5
                hp = 90
                hp_koef = 100
                role_id = 2
            else:
                povolani = 'obycejny clovek'
                dmg = 1
                dmg_koef = 1
                obrana = 1
                obrana_koef = 1
                hp = 1
                hp_koef = 1
                role_id = 4


            if test_question == True:
                chose_povolani = povolani
            else:
                chose_povolani = ""

            new_player = player.objects.create(
                active = True,
                name=i.name,
                gender = i.gender,
                profile_img=i.player_profile_img,
                skill_points=0,
                role_img_id = role_id,
                xp=0,
                lvl=1,
                score=0,
                energie=100,
                last_energy_update=timezone.now(),
                povolani=chose_povolani,
                dmg=dmg,
                dmg_koef=dmg_koef,
                dmg_now=dmg,
                armor=obrana,
                armor_koef=obrana_koef,
                armor_now=obrana,
                hp=hp,
                hp_koef=hp_koef,
                hp_now=hp,
                hp_actual_fight=hp,
                panak=0,
                maly_kelimek=0,
                velky_kelimek=0,
            )
            new_player.save()
            print(f"Vytvořen hráč: {new_player.name} s povoláním {new_player.povolani}")

            
        for p in player.objects.all():
            new_achivments = achievements.objects.create(
                player=p,
            )

        pocet = player.objects.count()
        pocet_hracu_instance = pocet_hracu.objects.first()
        pocet_hracu_instance.pocet_hracu_now = pocet
        pocet_hracu_instance.pocet_hracu_full = pocet
        pocet_hracu_instance.pocet_hracu_off = 0
        pocet_hracu_instance.save()
        print(f"Aktuální počet hráčů: {pocet}")

        
        
        first_boss = boss_names_descriptions.objects.get(patro=1)
        boss.objects.create(
            name = first_boss.name,
            boss_img = first_boss.boss_img,
            patro = 1,
            description = first_boss.description,
            defeated = False,
            lvl = 1,
            dmg = 15,
            armor = 5,
            hp = 200,
            reward_xp = 200
        )
        print("Vytvořen první boss.")
            

    return redirect('index')



def test(request):
    if request.method == 'POST':
        test_start = test_model.objects.first()
        test_start.test_status = True
        test_start.save()

        reset(request)
        print("PROBĚHLO PROMAZÁNÍ DATABÁZE")
        actual_patro = 1
        rounds = 1
        wins = 0
        lose = 0
        draw = 0
        actual_boss = boss.objects.filter(defeated=False).first()
        while actual_patro < 25 or actual_boss.name == 'KONEC HRY':
            actual_boss = boss.objects.filter(defeated=False).first()
            actual_patro = actual_boss.patro

            all_players = player.objects.all()
            for p in all_players:
                stat_up_test(request, p.id)
            
            
            fight(request)

            all_players = player.objects.all()
            for p in all_players:
                random_xp = random.randint(20, 100)
                p.add_xp(round(random_xp))
                p.save()
            rounds += 1
            print(f"Round {rounds} completed.")
            print(f"Aktuální patro: {actual_patro}")
            

            actual_fight = FightLog.objects.filter(boss=actual_boss).last()
            if actual_fight.outcome == 'players':
                wins += 1
            elif actual_fight.outcome == 'draw':
                draw += 1
            else:
                lose += 1

            

        all_players = player.objects.all()
        all_players = all_players.order_by('score').reverse()
        all_achivements = achievements.objects.all()
        all_achivements = all_achivements.order_by('total_dmg_delt').reverse()
        all_bosses = boss.objects.all()

        total_dmg_all = 0
        total_armor_all = 0

        for p in all_achivements:
            total_dmg_all += p.total_dmg_delt
            total_armor_all += p.total_dmg_taken

        pomer = p.total_dmg_delt / p.total_dmg_taken

        test_start.test_status = False
        test_start.save()

        return render(request, 'game/test_stats.html', context={
            'all_players': all_players,
            'all_achivements': all_achivements,
            'all_bosses': all_bosses,
            'rounds': rounds,
            'wins': wins,
            'lose': lose,
            'draw': draw,
            'total_dmg_all': total_dmg_all,
            'total_armor_all': total_armor_all,
            'pomer': pomer,
        })

def admin(request):
    return render(request, 'game/admin.html')


def active(request):
    all_players = player.objects.all()
    for p in all_players:
        p.active = True
        p.save()
    return redirect('index')

def deactive(request):
    all_players = player.objects.all()
    for p in all_players:
        p.active = False
        p.save()
    return redirect('index')


def stat_up_test(request, player_id):
    one_player = player.objects.get(id=player_id)
    while one_player.skill_points >= 1:
        print(f"Zvyšování statů pro hráče {one_player.name}, zbývající skill pointy: {one_player.skill_points}, povolání: {one_player.povolani}")

        if one_player.povolani == "mag":
            stat_type = random.choices(
                ['dmg', 'armor', 'hp'],
                weights=[0.6, 0.1, 0.3],
                k=1
            )[0]
        elif one_player.povolani == "valecnik":
            stat_type = random.choices(
                ['dmg', 'armor', 'hp'],
                weights=[0.2, 0.4, 0.4],
                k=1
            )[0]
        elif one_player.povolani == "hunter":
            stat_type = random.choices(
                ['dmg', 'armor', 'hp'],
                weights=[0.4, 0.3, 0.3],
                k=1
            )[0]

        if stat_type == 'dmg':
            random_dmg = random.uniform(0.8, 1.2)
            one_player.dmg_now += round(one_player.dmg_koef * random_dmg)
            one_player.skill_points -= 1
            one_player.save()
        elif stat_type == 'armor':
            random_armor = random.uniform(0.8, 1.2)
            one_player.armor_now += round(one_player.armor_koef * random_armor)
            one_player.skill_points -= 1
            one_player.save()

        elif stat_type == 'hp':
            random_hp = random.uniform(0.8, 1.2)
            one_player.hp_now += round(one_player.hp_koef * random_hp)
            one_player.hp_actual_fight += round(one_player.hp_koef * random_hp)
            one_player.skill_points -= 1
            one_player.save()
    
