from math import e
from operator import ne
from pickle import FALSE, TRUE
import random
from typing_extensions import Self
from django.shortcuts import render
from tutorialapp import models
from .models import boss, FightLog, TurnLog, boss_names_descriptions
from game.models import player, pocet_hracu, achievements, test_model
from django.db.models import Max


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

    # ODEČTENÍ ENERGIE:
    test_status = test_model.objects.first()
    if test_status.test_status== False:
        for p in players:
            p.energy_update(30)
    else:
        pass

    # --- INICIALIZACE LOGU BOJE ---
    # Vytvoření záznamu o celém boji
    fight_log = FightLog.objects.create(
        boss=actual_boss,
        player_count=pocet_hracu_now,
        # Ostatní statistiky a výsledek budou nastaveny na konci boje
    )
    turn_counter = 1
    dmg_round_bonus = 1.01
    total_player_dmg = 0
    total_boss_dmg = 0
    # -------------------------------



    while boss_hp > 0 and any(p.hp_actual_fight > 0 for p in players):
        

        players_iniciative = random.randint(1, 100)
        boss_iniciative = random.randint(1, 100)

        dmg_round_bonus += 0.02 # Postupné zvyšování bonusového poškození každým kolem

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

            # Zjištění kritického zásahu:
            critic_chance = current_player.critic_chance 
            critic_roll = random.uniform(0, 100)
            if critic_chance >= critic_roll:
                critic_status = True
                critic_dmg_bonus = 2
            else:
                critic_status = False
                critic_dmg_bonus = 1

            # Zjištění bojového postoje:
            doge_chance = actual_boss.dodge_chance
            dodge_roll = random.uniform(0, 100)
            if doge_chance >= dodge_roll:
                bojovy_postoj_status = True
                bojovy_postoj_bonus = 2
            else:
                bojovy_postoj_status = False
                bojovy_postoj_bonus = 1

            # Výpočet poškození hráče a brnění bosse s rozptylem
            current_player_dmg_roll = round(((current_player.dmg_now * (random.uniform(0.8, 1.2))) * dmg_round_bonus) * critic_dmg_bonus)
            boss_armor_roll = round((current_boss_armor * (random.uniform(0.9, 1.1))) * bojovy_postoj_bonus)
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

                critic_status=critic_status,
                bojovy_postoj_status=bojovy_postoj_status,
            )
            # Konec záznamu tahu hráče

            # ACHIEVEMENTS UPDATE
            player_achievement = achievements.objects.get(player=current_player)
            player_achievement.attack_counter += 1
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

            # Zjištění kritického zásahu:
            boss_critic_chance = actual_boss.critic_chance 
            boss_critic_roll = random.uniform(0, 100)

            if boss_critic_chance >= boss_critic_roll:
                critic_status = True
                critic_dmg_bonus = 2
            else:
                critic_status = False
                critic_dmg_bonus = 1

            # Zjištění bojového postoje:
            dodge_chance = target_player.dodge_chance
            dodge_roll = random.uniform(0, 100)
            if dodge_chance >= dodge_roll:
                bojovy_postoj_status = True
                bojovy_postoj_bonus = 2
            else:
                bojovy_postoj_status = False
                bojovy_postoj_bonus = 1



            # Výpočet poškození bosse a brnění hráče s rozptylem
            boss_dmg_roll = round(((current_boss_dmg * (random.uniform(0.8, 1.2))) * dmg_round_bonus) * critic_dmg_bonus)
            target_player_armor_roll = round((target_player.armor_now * (random.uniform(0.9, 1.1))) * bojovy_postoj_bonus) 

            dmg_delt = boss_dmg_roll - target_player_armor_roll
            
            if dmg_delt < 0:
                dmg_delt = 0
                
            target_player.hp_actual_fight -= dmg_delt
            target_player.save() # Uložení nového HP hráče
            total_boss_dmg += dmg_delt # Sčítáme celkové poškození
            
            if target_player.hp_actual_fight <= 0:
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

                critic_status=critic_status,
                bojovy_postoj_status=bojovy_postoj_status,
            )
            # Konec záznamu tahu bosse
            
            # ACHIEVEMENTS UPDATE
            player_achievement = achievements.objects.get(player=target_player)
            player_achievement.attack_get += 1

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
        print("HRÁČI vyhráli!")

        actual_boss.defeated = True
        actual_boss.save()
    else:
        winner = "boss"
        print("BOSS vyhrál!")

        
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
        next_reward = round(actual_boss.reward_xp * 1.1)
        reward_limit = ((patro * 2) * 10)
        if next_reward < reward_limit:
            next_reward = reward_limit
        hraci = pocet_hracu.objects.first()
        pocet_hracu_now = hraci.pocet_hracu_now
        next_criti_chance = actual_boss.lvl * 1.5
        if next_criti_chance > 50:
            next_criti_chance = 50
        next_dodge_chance = actual_boss.lvl * 1.5
        if next_dodge_chance > 50:
            next_dodge_chance = 50
        
        all_skill_points = 0

        for p in players:
            p.add_xp(actual_boss.reward_xp)
            all_skill_points += p.skill_points
            p.save()

# POJISTKA KDYBY HRÁČI NEVYLEPŠOVALI POSTAVY

        prum_skill_points = round(all_skill_points / pocet_hracu_now)

        if prum_skill_points <= 3:
            skill_point_balance = 1.0
        elif prum_skill_points <= 6:
            skill_point_balance = 1.1
        elif prum_skill_points <= 9:
            skill_point_balance = 1.4
        elif prum_skill_points <= 12:
            skill_point_balance = 1.8
        elif prum_skill_points <= 15:
            skill_point_balance = 2.5
        else:
            pass
        
        print(f"Skill point balance pro nového bosse: {skill_point_balance} (průměrný skill point hráče: {prum_skill_points})")

        dmg = round(((hraci.all_players_dmg / pocet_hracu_now) * 1.1) * skill_point_balance)
        armor = round(((hraci.all_players_armor / pocet_hracu_now) * 0.8) * skill_point_balance)
        hp = round(((hraci.all_player_hp * 0.85)) * skill_point_balance)

# POJISTKA ABY NÁSLEDUJÍCÍ BOS BYL VŽDYCKY SILNĚJŠÍ NEŽ PŘEDCHOZÍ

        actual_dmg = actual_boss.dmg
        actual_armor = actual_boss.armor
        actual_hp = actual_boss.hp

        if dmg < actual_dmg:
            dmg = actual_boss.dmg * 1.1
            print("POJISTKA DMG AKTIVOVÁNA")
        if armor < actual_armor:
            armor = actual_boss.armor * 1.1
            print("POJISTKA ARMOR AKTIVOVÁNA")
        if hp < actual_hp:
            hp = actual_boss.hp * 1.1
            print("POJISTKA HP AKTIVOVÁNA")


        boss.objects.create(
            name = next_boss_info.name,
            patro = next_patro,
            description = next_boss_info.description,
            boss_img = next_boss_info.boss_img,
            defeated = False,
            lvl = next_lvl,

            dmg = dmg,
            armor = armor,
            hp = hp,

            critic_chance = next_criti_chance,
            dodge_chance = next_dodge_chance,

            reward_xp = round(next_reward)
        )
        print("nový BOSS vytbořen:")
        print("Patro:", next_patro)
        print("Jméno:", next_boss_info.name)
        print("Úroveň:", next_lvl)
        print("DMG:", dmg)
        print("Armor:", armor)
        print("HP:", hp)
        print("Odměna XP:", round(next_reward))

    


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
    low_energy_players = energy_request.filter(energie__lt=30)

    start_status = False

    actual_patro = actual_boss.patro
    for p in energy_request:
        if p.energie < 30:
            print("Hráč", p.name, "nemá dostatek energie:", p.energie)
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
        "low_energy_players": low_energy_players,
        "actual_patro": actual_patro,

        
    })