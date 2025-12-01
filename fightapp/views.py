import random
from typing import Self
from django.shortcuts import render
from tutorialapp import models
from .models import boss, FightLog, TurnLog, boss_names_descriptions
from game.models import player, pocet_hracu, achievements
from django.db.models import Max


def fight(request):
    if request.method == "POST":
        print("Zápas probíhá...")
        boss_id = request.POST.get("boss_id")
        print("Boss ID:", boss_id)
        
    # Načtení dat a inicializace
    actual_boss = boss.objects.filter(id=boss_id).first()
    patro = actual_boss.patro
    boss_dmg_base = actual_boss.dmg # Uložení základní hodnoty DMG bosse
    boss_armor_base = actual_boss.armor # Uložení základní hodnoty Armor bosse
    
    # Dynamické HP bosse
    pocet_hracu_now = pocet_hracu.objects.first().pocet_hracu_now 
    boss_hp = (actual_boss.hp * pocet_hracu_now) * 0.8
    
    # Inicializace proměnných pro boj
    players = player.objects.filter(active=True)
    
    print("Boss name: ", actual_boss.name, "Boss stats - Dmg:", boss_dmg_base, "Armor:", boss_armor_base, "HP:", boss_hp)
    print("Do boje nastupují hráči:")

    for p in players:
        print("Hráč:", p.name, "Dmg:", p.dmg_now, "Armor:", p.armor_now, "HP:", p.hp_now)

    # --- INICIALIZACE LOGU BOJE ---
    # Vytvoření záznamu o celém boji
    fight_log = FightLog.objects.create(
        boss=actual_boss,
        player_count=pocet_hracu_now,
        # Ostatní statistiky a výsledek budou nastaveny na konci boje
    )
    turn_counter = 1
    total_player_dmg = 0
    total_boss_dmg = 0
    # -------------------------------

    players_iniciative = random.randint(1, 100)
    boss_iniciative = random.randint(1, 100)

    while boss_hp > 0 and any(p.hp_actual_fight > 0 for p in players):
        
        # Hodnoty, které se dynamicky mění v rámci TAHU (pro výpočet brnění/DMG roll)
        current_boss_armor = boss_armor_base
        current_boss_dmg = boss_dmg_base

        if players_iniciative >= boss_iniciative:
            # TAH HRÁČE
            
            # Filtrování mrtvých hráčů
            live_players = players.filter(hp_actual_fight__gt=0)
            if not live_players.exists():
                break # Všichni hráči jsou mrtví, konec boje
                
            current_player = random.choice(live_players) 
            
            print("Hráč", current_player.name, "zaútočí jako první!" "stats - Dmg:", current_player.dmg_now, "Armor:", current_player.armor_now, "HP:", current_player.hp_actual_fight)

            # Výpočet poškození hráče a brnění bosse s rozptylem
            current_player_dmg_roll = round(current_player.dmg_now * (random.uniform(0.8, 1.2)))
            boss_armor_roll = round(current_boss_armor * (random.uniform(0.9, 1.1)))
            dmg_delt = current_player_dmg_roll - boss_armor_roll

            if dmg_delt < 0:
                dmg_delt = 0
            

            boss_hp -= dmg_delt
            total_player_dmg += dmg_delt # Sčítáme celkové poškození
            
            # ZÁZNAM TAHU HRÁČE
            TurnLog.objects.create(
                fight=fight_log,
                turn_number=turn_counter,
                attacker_is_boss=False,
                attacker_player=current_player,
                target_player=None, # Cílem je boss
                damage_dealt=dmg_delt,
                attacker_damage_roll=current_player_dmg_roll, 
                target_armor_roll=boss_armor_roll,
                boss_hp_after=max(0, boss_hp), # Ujistíme se, že HP není záporné
                target_player_hp_after=current_player.hp_actual_fight, # HP hráče se nemění, ale zaznamenáme aktuální
            )
            # Konec záznamu tahu hráče

            # ACHIEVEMENTS UPDATE
            player_achievement = achievements.objects.get(player=current_player)

            dmg_record = achievements.objects.filter(player=current_player).aggregate(Max('best_dmg_delt'))['best_dmg_delt__max'] or 0

            player_achievement.total_dmg_delt += dmg_delt
            if dmg_delt > dmg_record:
                player_achievement.best_dmg_delt = dmg_delt
            else:
                pass
            player_achievement.save()


            print("Hráč", current_player.name, "udělil bossovi", dmg_delt, "poškození! Boss má nyní", max(0, boss_hp), "HP.")

        else:
            # TAH BOSSE
            print("Boss", actual_boss.name, "zaútočí jako první!")

            # Filtrování mrtvých hráčů
            live_players = players.filter(hp_actual_fight__gt=0)
            if not live_players.exists():
                break # Všichni hráči jsou mrtví, konec boje
                
            target_player = random.choice(live_players) 
            print("Boss útočí na hráče", target_player.name, "stats - Dmg:", target_player.dmg_now, "Armor:", target_player.armor_now, "HP:", target_player.hp_actual_fight)

            # Výpočet poškození bosse a brnění hráče s rozptylem
            boss_dmg_roll = round(current_boss_dmg * (random.uniform(0.8, 1.2)))
            target_player_armor_roll = round(target_player.armor_now * (random.uniform(0.9, 1.1))) 
            dmg_delt = boss_dmg_roll - target_player_armor_roll
            
            if dmg_delt < 0:
                dmg_delt = 0
                
            target_player.hp_actual_fight -= dmg_delt
            target_player.save() # Uložení nového HP hráče
            total_boss_dmg += dmg_delt # Sčítáme celkové poškození
            
            # ZÁZNAM TAHU BOSSE
            TurnLog.objects.create(
                fight=fight_log,
                turn_number=turn_counter,
                attacker_is_boss=True,
                attacker_player=None, # Útočník je boss
                target_player=target_player,
                damage_dealt=dmg_delt,
                attacker_damage_roll=boss_dmg_roll, 
                target_armor_roll=target_player_armor_roll,
                boss_hp_after=max(0, boss_hp), # HP bosse se nemění, ale zaznamenáme aktuální
                target_player_hp_after=max(0, target_player.hp_actual_fight),
            )
            # Konec záznamu tahu bosse
            
            # ACHIEVEMENTS UPDATE
            player_achievement = achievements.objects.get(player=target_player)

            # POZOR! DO UDRŽENÉHO POŠKOZENÍ SE NEPOČÍTÁ ARMOR, PROTOŽE TANKOVÉ BY JINAK PARADOXNĚ MĚLI NEJMENŠÍ HODNOTY
            
            player_achievement.total_dmg_taken += boss_dmg_roll
            player_achievement.save()

            print("Boss", actual_boss.name, "udělil hráči", target_player.name, "poškození", dmg_delt, "! Hráč má nyní", max(0, target_player.hp_actual_fight), "HP.")

        # Inkrementace čítače tahu a nové iniciativy
        turn_counter += 1
        players_iniciative = random.randint(1, 100)
        boss_iniciative = random.randint(1, 100)

    # --- VYHODNOCENÍ VÍTĚZE A AKTUALIZACE LOGU ---
    if boss_hp <= 0:
        winner = "players"
        print("Boss", actual_boss.name, "byl poražen!")
        actual_boss.defeated = True
        actual_boss.save()
    else:
        winner = "boss"
        print("Všichni hráči byli poraženi! Boss", actual_boss.name, "vítězí!")
        
    # Aktualizace hlavního záznamu boje
    fight_log.outcome = winner
    fight_log.final_boss_hp = max(0, boss_hp)
    fight_log.total_damage_dealt_by_players = total_player_dmg
    fight_log.total_damage_received_by_players = total_boss_dmg
    fight_log.save()
    # ---------------------------------------------

    # VĚCI PO BOJI:
    for p in players:
        p.hp_actual_fight = p.hp_now
        p.score_counter()
        p.save()

    turn_log = TurnLog.objects.filter(fight=fight_log).order_by('damage_dealt')

    if winner == "players":
        # Vytvoření dalšího bosse
        next_patro = patro + 1
        boss_names = boss_names_descriptions.objects.get(patro=next_patro).name
        next_lvl = actual_boss.lvl + 1
        next_reward = actual_boss.reward_xp * 1.2
        hraci = pocet_hracu.objects.first()
        pocet_hracu_now = hraci.pocet_hracu_now
        hraci.all_stats_counter()

        boss.objects.create(
            name = boss_names,
            patro = next_patro,
            description = "Lorem Ipsum",
            defeated = False,
            lvl = next_lvl,
            dmg = ((hraci.all_players_dmg) / pocet_hracu_now) * 1.1,
            armor = ((hraci.all_players_armor) / pocet_hracu_now) * 1.1,
            hp = ((hraci.all_players_hp) / pocet_hracu_now) * 1.1,
            reward_xp = next_reward
        )
        print(f"Nový boss: {boss_names} Patro: {next_patro} Level: {next_lvl} Reward XP: {next_reward}"),
    
        for p in players:
            p.add_xp(actual_boss.reward_xp)
            p.save()

    return render(request, 'fightapp/fight.html', context={
        # Zde můžete přidat fight_log.id nebo fight_log pro zobrazení výsledků v šabloně
        "fight_log": fight_log,
        "turn_logs": turn_log
    })


def dungeon(request):

    all_boss = boss.objects.all()
    actual_boss = all_boss.filter(defeated=False).first()
    print("Aktuální soupeř:", actual_boss)


    return render(request, 'fightapp/dungeon.html', context={
        "actual_boss": actual_boss,
        "all_boss": all_boss
    })