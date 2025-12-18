from math import e
from operator import ne
from pickle import FALSE, TRUE
import random
from typing import Self
from django.shortcuts import render
from tutorialapp import models
from .models import boss, FightLog, TurnLog, boss_names_descriptions
from game.models import player, pocet_hracu, achievements
from django.db.models import Max
from colorama import init, Fore, Style


def fight(request):
    if request.method == "POST":

        boss_id = request.POST.get("boss_id")
        if not boss_id:
            boss_id = boss.objects.filter(defeated=False).first().id


        
    # Načtení dat a inicializace
    actual_boss = boss.objects.filter(id=boss_id).first()
    patro = actual_boss.patro
    boss_dmg_base = actual_boss.dmg # Uložení základní hodnoty DMG bosse
    boss_armor_base = actual_boss.armor # Uložení základní hodnoty Armor bosse
    
    # Dynamické HP bosse
    pocet_hracu_now = pocet_hracu.objects.first().pocet_hracu_now 
    boss_hp = actual_boss.hp
    
    # Inicializace proměnných pro boj
    players = player.objects.filter(active=True)

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

                boss_max_hp=actual_boss.hp,
                boss_hp_after=max(0, boss_hp), # Ujistíme se, že HP není záporné
                target_player_hp_after=current_player.hp_actual_fight, # HP hráče se nemění, ale zaznamenáme aktuální
                target_player_max_hp=current_player.hp_now,
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


        else:
            # TAH BOSSE


            # Filtrování mrtvých hráčů
            live_players = players.filter(hp_actual_fight__gt=0)
            if not live_players.exists():
                break # Všichni hráči jsou mrtví, konec boje
                
            target_player = random.choice(live_players) 

            # Výpočet poškození bosse a brnění hráče s rozptylem
            boss_dmg_roll = round(current_boss_dmg * (random.uniform(0.8, 1.2)))
            target_player_armor_roll = round(target_player.armor_now * (random.uniform(0.9, 1.1))) 
            dmg_delt = boss_dmg_roll - target_player_armor_roll
            
            if dmg_delt < 0:
                dmg_delt = 0
                
            target_player.hp_actual_fight -= dmg_delt
            target_player.save() # Uložení nového HP hráče
            total_boss_dmg += dmg_delt # Sčítáme celkové poškození
            
            if target_player.hp_actual_fight <= 0:
                print(Fore.RED + f"Hráč {target_player.name} byl poražen!" + Style.RESET_ALL)
                player_achievement = achievements.objects.get(player=target_player)
                player_achievement.death_counter += 1
                player_achievement.save()

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
                boss_max_hp=actual_boss.hp,
                target_player_hp_after=max(0, target_player.hp_actual_fight),
                target_player_max_hp=target_player.hp_now,
            )
            # Konec záznamu tahu bosse
            
            # ACHIEVEMENTS UPDATE
            player_achievement = achievements.objects.get(player=target_player)

            # POZOR! DO UDRŽENÉHO POŠKOZENÍ SE NEPOČÍTÁ ARMOR, PROTOŽE TANKOVÉ BY JINAK PARADOXNĚ MĚLI NEJMENŠÍ HODNOTY
            
            player_achievement.total_dmg_taken += target_player_armor_roll
            player_achievement.save()

        # Inkrementace čítače tahu a nové iniciativy
        turn_counter += 1
        players_iniciative = random.randint(1, 100)
        boss_iniciative = random.randint(1, 100)

    # --- VYHODNOCENÍ VÍTĚZE A AKTUALIZACE LOGU ---
    if boss_hp <= 0:
        winner = "players"
        print(Fore.GREEN + "Boss", actual_boss.name, "byl poražen!" + Style.RESET_ALL)
        actual_boss.defeated = True
        actual_boss.save()
    else:
        winner = "boss"
        print(Fore.RED + "Boss", actual_boss.name, "vítězí!" + Style.RESET_ALL)
        
    # Aktualizace hlavního záznamu boje
    fight_log.outcome = winner
    fight_log.final_boss_hp = max(0, boss_hp)
    fight_log.total_damage_dealt_by_players = total_player_dmg
    fight_log.total_damage_received_by_players = total_boss_dmg
    fight_log.save()
    # ---------------------------------------------

    # VĚCI PO BOJI:
    hraci = pocet_hracu.objects.first()
    hraci.all_stats_counter()

    for p in players:
        p.hp_actual_fight = p.hp_now
        p.score_counter()
        p.save()

    turn_log = TurnLog.objects.filter(fight=fight_log).order_by('turn_number')

    if winner == "players":
        # Vytvoření dalšího bosse
        next_patro = patro + 1
        next_boss_info = boss_names_descriptions.objects.get(patro=next_patro)
        next_lvl = actual_boss.lvl + 1
        next_reward = actual_boss.reward_xp * 1.1
        hraci = pocet_hracu.objects.first()
        pocet_hracu_now = hraci.pocet_hracu_now
        print("Počet hráčů nyní:", pocet_hracu_now)
        

        for p in players:
            p.add_xp(actual_boss.reward_xp)
            p.save()

        boss.objects.create(
            name = next_boss_info.name,
            patro = next_patro,
            description = next_boss_info.description,
            boss_img = next_boss_info.boss_img,
            defeated = False,
            lvl = next_lvl,

            dmg = ((hraci.all_players_dmg) / pocet_hracu_now) + (actual_boss.dmg),
            armor = ((hraci.all_players_armor) / pocet_hracu_now) + (actual_boss.armor),
            hp = ((hraci.all_player_hp) / pocet_hracu_now) + (actual_boss.hp),

            reward_xp = round(next_reward)
        )
        print(f"Nový boss: {next_boss_info.name} Patro: {next_patro} Level: {next_lvl} Reward XP: {next_reward}"),
    


    return render(request, 'fightapp/fight.html', context={
        # Zde můžete přidat fight_log.id nebo fight_log pro zobrazení výsledků v šabloně
        "fight_log": fight_log,
        "turn_logs": turn_log
    })





def dungeon(request):

    all_boss = boss.objects.all()   
    actual_boss = all_boss.filter(defeated=False).first()
    actual_boss_img = boss_names_descriptions.objects.get(patro=actual_boss.patro).boss_img

    energy_request = player.objects.filter(active=True)
    low_energy_players = energy_request.filter(energie__lt=50)

    start_status = False

    for p in energy_request:
        if p.energie < 50:
            print("Hráč", p.name, "má nedostatek energie:", p.energie)
            start_status = False
            break
        else:
            start_status = True
            print("Hráč", p.name, "má dostatek energie:", p.energie)
 

    print("Aktuální soupeř:", actual_boss)
    print("Startovní status:", start_status)


    return render(request, 'fightapp/dungeon.html', context={
        "actual_boss_img": actual_boss_img,
        "actual_boss": actual_boss,
        "all_boss": all_boss,
        "start_status": start_status,
        "low_energy_players": low_energy_players

        
    })