from django.shortcuts import render
from game.models import player, pocet_hracu, achievements


# TADY PROBÍHÁ TAKOVÁ REGISTRACE HRÁČE A JEHO VÝBĚR POVOLÁNÍ

def tut_end(request):

    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        povolani = request.POST.get('povolani')
        print(player_id, povolani)

        if povolani == 'mag':
            dmg = 18
            # dmg_koef = 9 (původní hodnota)
            dmg_koef = 18
            obrana = 2
            obrana_koef = 0.5
            hp = 70
            hp_koef = 18
        elif povolani == 'valecnik': 
            dmg = 12
            # dmg_koef = 4
            dmg_koef = 8
            obrana = 10
            obrana_koef = 2.2
            hp = 120
            hp_koef = 35
        elif povolani == 'hunter':
            dmg = 14
            # dmg_koef = 6
            dmg_koef = 12
            obrana = 6
            obrana_koef = 1.5
            hp = 90
            hp_koef = 24
        else:
            povolani = 'obycejny clovek'
            dmg = 1
            dmg_koef = 1
            obrana = 1
            obrana_koef = 1
            hp = 1
            hp_koef = 1

        chosen_player = player.objects.get(id=player_id)
        # NASTAVENÍ ZÁKLADNÍCH HODNOT
        chosen_player.dmg = dmg
        chosen_player.dmg_koef = dmg_koef
        chosen_player.armor = obrana
        chosen_player.armor_koef = obrana_koef
        chosen_player.hp = hp
        chosen_player.hp_koef = hp_koef
        chosen_player.povolani = povolani

        # NASTAVENÍ HODNOT PRO LVL 1
        chosen_player.dmg_now = dmg
        chosen_player.dmg_koef = dmg_koef
        chosen_player.armor_now = obrana
        chosen_player.armor_koef = obrana_koef
        chosen_player.hp_now = hp
        chosen_player.hp_koef = hp_koef
        chosen_player.hp_actual_fight = hp
        chosen_player.povolani = povolani

        #Aktivace hráče:
        chosen_player.active = True
        chosen_player.save()

        #Založení achievemts pro hráče
        achievements.objects.create(
            player=chosen_player,
            best_dmg_delt=0,
            total_dmg_delt=0,
            total_dmg_taken=0,
        )

        # aktuální počet hráčů (uděláno dementně ale nechtělo se mi s tím srát)
        pocet_hracu_full = player.objects.all().count()
        pocet_hracu_off = player.objects.filter(active=False).count()
        pocet_hracu_now = pocet_hracu_full - pocet_hracu_off

        print("POCET HRACU FULL:", pocet_hracu_full)
        print("POCET HRACU OFF:", pocet_hracu_off)
        print("POCET HRACU NOW:", pocet_hracu_now)

        pocet_hracu_data = pocet_hracu.objects.first()
        pocet_hracu_data.pocet_hracu_now = pocet_hracu_now
        pocet_hracu_data.pocet_hracu_full = pocet_hracu_full
        pocet_hracu_data.pocet_hracu_off = pocet_hracu_off

        pocet_hracu_data.save()

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