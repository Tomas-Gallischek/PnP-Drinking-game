from django.shortcuts import render
from game.models import jmena_hracu, player, pocet_hracu, achievements
from django.utils import timezone


# TADY PROBÍHÁ TAKOVÁ REGISTRACE HRÁČE A JEHO VÝBĚR POVOLÁNÍ

def tut_end(request):

    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        povolani = request.POST.get('povolani')
        print(player_id, povolani)

        if povolani == 'mag':
            dmg = 20
            dmg_koef = 40
            obrana = 5
            obrana_koef = 5
            hp = 70
            hp_koef = 100
            role_id = 1
        elif povolani == 'valecnik': 
            dmg = 10
            dmg_koef = 25
            obrana = 15
            obrana_koef = 15
            hp = 120
            hp_koef = 300
            role_id = 3
        elif povolani == 'hunter':
            dmg = 14
            dmg_koef = 33
            obrana = 10
            obrana_koef = 10
            hp = 90
            hp_koef = 200
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

        
        this_player = player.objects.get(id=player_id)
        chosen_player = jmena_hracu.objects.get(name=this_player.name)

        this_player.active = True
        this_player.name = chosen_player.name
        this_player.gender = chosen_player.gender
        this_player.profile_img = chosen_player.player_profile_img
        this_player.skill_points = 0
        this_player.role_img_id = role_id
        this_player.xp = 0
        this_player.lvl = 1
        this_player.score = 0
        this_player.energie = 100
        this_player.last_energy_update = timezone.now()
        this_player.povolani = povolani
        this_player.dmg = dmg
        this_player.dmg_koef = dmg_koef
        this_player.dmg_now = dmg
        this_player.armor = obrana
        this_player.armor_koef = obrana_koef
        this_player.armor_now = obrana
        this_player.hp = hp
        this_player.hp_koef = hp_koef
        this_player.hp_now = hp
        this_player.hp_actual_fight = hp
        this_player.panak = 0
        this_player.maly_kelimek = 0
        this_player.velky_kelimek = 0

        this_player.save()

        print(f"Vytvořen hráč: {this_player.name} s povoláním {this_player.povolani}")

        #Založení achievemts pro hráče
        achievements.objects.create(
            player=this_player,
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
        "chosen_player": this_player,
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
    filtred_players = all_players.filter(povolani="")

    for p in filtred_players:
        p.active = False
        achievements.objects.filter(player=p).delete()
        p.save()
        
    

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