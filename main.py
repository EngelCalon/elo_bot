import discord
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from datetime import date

# Charger les variables du fichier .env
load_dotenv()
history_file = os.getenv("HISTORY_FILE")
players_elo_file = os.getenv("PLAYERS_ELO_FILE")
bot_seed = os.getenv("BOT_SEED")

if not os.path.exists(history_file):
    df = pd.DataFrame(columns=[ 'id',
                                'mode',
                               'team_A_p1', 'team_A_p1_pick',
                                'team_A_p2', 'team_A_p2_pick',
                                'team_A_p3', 'team_A_p3_pick',
                                'team_B_p1', 'team_B_p1_pick',
                                'team_B_p2', 'team_B_p2_pick',
                                'team_B_p3', 'team_B_p3_pick',
                                'date_time',
                                'result'])
    df.to_csv(history_file, index=False, sep= ';')


if not os.path.exists(players_elo_file):
    df = pd.DataFrame(columns=['id', 'player', 'general_elo', '1v1_elo', '2v2_elo', '3v3_elo', 'date_time'])
    df.to_csv(players_elo_file, index=False, sep= ';')

history = pd.read_csv(history_file)
players_elo = pd.read_csv(players_elo_file)

def prob_A_win(eloA: float, eloB:float )-> float:
    return 1 / (1 + 10**((eloB - eloA) / 400))

def get_new_rating(eloA: float, eloB: float, result: bool, k=32) -> float:
    return eloA + k * (result - prob_A_win(eloA, eloB))

def set_player_elo(player: str, mode: str, new_elo: float):
    if player not in players_elo['player'].values:
        players_elo = players_elo.append({'id': players_elo['id'].max() +1 ,'player': player, 'general_elo': 1000, '1v1_elo': 1000, '2v2_elo': 1000, '3v3_elo': 1000, 'date_time': date.today()}, ignore_index=True)
    #ECRIRE LES LIGNES POUR AJOUTER LE ELO EN FONCTION DU MODE


    players_elo.to_csv(players_elo_file, index=False)


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
@client.event
async def on_ready():
    print("Je suis bien prêt !")

@client.event
async def on_message(message):
    if message.content.startswith("!elo"):
        parts = message.content.split(" ")
        if len(parts) != 4:
            await message.channel.send("Non d'un petit bonhomme!\n !elo @user1 @user2 result (1 si le joueur 1 gagne, 0 si le joueur 2 gagne)")
            return
        j1 = parts[1]
        j2 = parts[2]
        result = int(parts[3])
        if result != 0 and result != 1:
            await message.channel.send("Tu m'as pris pour un jambon ! Le résultat doit être 0 ou 1")
            return
        elo1 = 1000
        elo2= 1200
        j1_new_el = get_new_rating(elo1, elo2, result)
        j2_new_el = get_new_rating(elo2, elo1, 1 - result)
        await message.channel.send(f"Les nouveaux ELOs sont {j1_new_el} pour {j1} et {j2_new_el} pour {j2}")
        


client.run(bot_seed)

