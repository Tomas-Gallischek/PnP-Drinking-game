import random
from django.shortcuts import render
from . models import boss
from game.models import player, pocet_hracu


def fight(request):
    if request.method == "POST":
        print("Zápas probíhá...")
        boss_id = request.POST.get("boss_id")
        print("Boss ID:", boss_id)

    actual_boss = boss.objects.filter(id=boss_id).first()
    boss_dmg = actual_boss.dmg
    boss_armor = actual_boss.armor

    # POZOR! JEDINÉ HP SE MĚNÍ DYNAMICKY PODLE POČTU HRÁČŮ
    pocet_hracu_now = pocet_hracu.objects.first().pocet_hracu_now 
    boss_hp = actual_boss.hp * pocet_hracu_now
    print("Boss name: ", actual_boss.name, "Boss stats - Dmg:", boss_dmg, "Armor:", boss_armor, "HP:", boss_hp)

    players = player.objects.filter(active=True)
    print("Do boje nastupují hráči:")
    for p in players:
        print("Hráč:", p.name, "Dmg:", p.dmg_now, "Armor:", p.armor_now, "HP:", p.hp_now)

    players_iniciative = random.randint(1, 100)
    boss_iniciative = random.randint(1, 100)

    while boss_hp >= 0 and any(p.hp_actual_fight >= 0 for p in players):
        if players_iniciative >= boss_iniciative:

            current_player = random.choice(players.filter(hp_actual_fight__gt=0)) # <-- filtrace mrtvých hráčů
            print("Hráč", current_player.name, "zaútočí jako první!" "stats - Dmg:", current_player.dmg_now, "Armor:", current_player.armor_now, "HP:", current_player.hp_actual_fight)

            current_player_dmg = round(current_player.dmg_now * (random.uniform(0.8, 1.2))) # <-- 20% rozptyl pro všechny stejný
            boss_armor = round(boss_armor * (random.uniform(0.9, 1.1))) # <-- 10% rozptyl pro všechny stejný
            dmg_delt = current_player_dmg - boss_armor

            if dmg_delt < 0:
                dmg_delt = 0
            boss_hp -= dmg_delt
            print("Hráč", current_player.name, "udělil bossovi", dmg_delt, "poškození! Boss má nyní", boss_hp, "HP.")

        else:
            print("Boss", actual_boss.name, "zaútočí jako první!")

            target_player = random.choice(players.filter(hp_actual_fight__gt=0)) # <-- filtrace mrtvých hráčů

            print("Boss útočí na hráče", target_player.name, "stats - Dmg:", target_player.dmg_now, "Armor:", target_player.armor_now, "HP:", target_player.hp_actual_fight)

            boss_dmg = round(boss_dmg * (random.uniform(0.8, 1.2))) # <-- 20% rozptyl pro všechny stejný
            target_player_armor = round(target_player.armor_now * (random.uniform(0.9, 1.1))) # <-- 10% rozptyl pro všechny stejný
            dmg_delt = boss_dmg - target_player_armor
            if dmg_delt < 0:
                dmg_delt = 0
            target_player.hp_actual_fight -= dmg_delt
            target_player.save()
            print("Boss", actual_boss.name, "udělil hráči", target_player.name, "poškození", dmg_delt, "! Hráč má nyní", target_player.hp_actual_fight, "HP.")

    # Vyhodnocení vítěze
    if boss_hp <= 0:
        winner = "players"
        print("Boss", actual_boss.name, "byl poražen!")
        actual_boss.defeated = True
        actual_boss.save()
    else:
        winner = "boss"
        print("Všichni hráči byli poraženi! Boss", actual_boss.name, "vítězí!")

    # Reset HP hráčů po boji
    for p in players:
        p.hp_actual_fight = p.hp_now
        p.save()


    return render(request, 'fightapp/fight.html', context={

    })


def dungeon(request):

    all_boss = boss.objects.all()
    actual_boss = all_boss.filter(defeated=False).first()
    print("Aktuální soupeř:", actual_boss)


    return render(request, 'fightapp/dungeon.html', context={
        "actual_boss": actual_boss,
        "all_boss": all_boss
    })