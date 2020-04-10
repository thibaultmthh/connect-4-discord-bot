import numpy as np
import random
import discord
import pandas as pd
import time
import random
from discord.ext import tasks
client = discord.Client()

games_en_cours = {}

usefull = ["user_id","adversaires_user_ids","jeu","temps_partie","timestamp"]
try:
    dfGames = pd.read_csv("data/BDD_scores.csv")[usefull]
except:
    dfGames = pd.DataFrame({"user_id":[], "adversaires_user_ids":[], "jeu": [],"temps_partie": [],"timestamp":[]})
    dfGames.to_csv('data/BDD_scores.csv')





with open("token.txt","r") as f:
    token = f.readline().replace("\n","")


class Puissance4():
    def __init__(self, shape=(6, 7)):
        self.grille = np.zeros(shape)

    def get_plateau(self):
        return self.grille

    def get_column(self, nb_column):
        column = []
        for ligne in self.grille:
            column.append(ligne[nb_column])
        return column

    def get_all_diag(self):
        diagonales = []
        for x in range(0 - self.grille.shape[0] + 1, self.grille.shape[1]):
            diagonales.append(np.diag(self.grille, k=x))
            diagonales.append(np.diag(np.fliplr(self.grille), k=x))
        return diagonales

    def get_all_columns(self):
        columns = []
        for x in range(self.grille.shape[1]):
            columns.append(self.get_column( x))
        return columns

    def insert_column(self, nb_column, value):
        a = 0
        for ligne in self.grille:
            ligne[nb_column] = value[a]
            self.grille[a] = ligne
            a += 1

    def check_victory(self):
        list_combinaison = self.get_all_columns()

        for s in self.get_all_diag():
            list_combinaison.append(s)
        for s in self.grille:
            list_combinaison.append(s)
        for liste in list_combinaison:
            last_val = 0
            nb = 1
            for val in liste:
                if last_val == val and val != 0:
                    nb += 1
                else:
                    nb = 1
                if nb >= 4:
                    return True, last_val
                last_val = int(val)
        return False, 0

    def add_pion(self, nb_column, pion_value=1):
        base_column = self.get_column(nb_column)
        out_column = np.copy(base_column)
        if base_column[-1] == 0: #si c'est le premier pion
            out_column[-1] = pion_value
            self.insert_column(nb_column, out_column)
            return True
        if base_column[0] != 0:
            return False
        for index, value in enumerate(base_column):
            if value != 0:
                if index == 0:
                    return False
                else:
                    out_column[index - 1] = pion_value
                    break
        self.insert_column(nb_column, out_column)
        return True

class truc_de_merde_flemme_de_resoudre_lerreur():
    def __init__(self):
        self.id =0
class Game():
    def __init__(self, playersID, shape=(6, 7), name="base"):
        self.playersID = []
        for playerID in playersID:
            self.playersID.append(playerID.id)
        self.game = Puissance4(shape)
        self.shape = shape
        self.name = name
        self.last_played = 0
        self.id_message_reaction = truc_de_merde_flemme_de_resoudre_lerreur()
        self.id_message_grille = truc_de_merde_flemme_de_resoudre_lerreur()
        self.column_played = 0
        self.player_had_play = 0
        self.timestamp_start = time.time()

    def get_game(self):
        return self.game.get_plateau()

    def get_turn_player(self):
        return self.playersID[self.last_played]

    def jouer(self, id, column):
        if id not in self.playersID:
            return "Tu n'est pas inscris dans cette partie"

        if id != self.playersID[self.last_played]:
            return "Ohh doucement, attend ton tour, C'est actuelement le tour de <@{}>".format(self.playersID[self.last_played])
        self.column_played = column
        pion_value = 0
        for n, pID in enumerate(self.playersID):
            if pID == id:
                pion_value = n + 1
        if self.game.add_pion(column, pion_value):

            self.player_had_play = self.playersID[self.last_played]
            if len(self.playersID)-1 == self.last_played:
                self.last_played = 0
            else:
                self.last_played +=1
            return "A toi de jouer <@{}>".format(self.playersID[self.last_played])
        else:
            return "<@{}> La colone est pleine, Rejoue sur une autre".format(self.playersID[self.last_played])
    def check_winner(self):
        r = self.game.check_victory()
        vainqueur = "A <@{}>".format(self.playersID[self.last_played])
        e = 0
        if r[0]:
            vainqueur = self.playersID[r[1]-1]
            e = {"user_id":vainqueur, "adversaires_user_ids":self.playersID, "jeu": "x4","temps_partie": (time.time() - self.timestamp_start),"timestamp":time.time()}
        return r[0], vainqueur , e



def supprime_game(nom):
    try:
        del games_en_cours[nom]
        return True
    except:
        return False


async def affiche_game(game, new, chanel = None):
    couleurs = "⚪🔵🔴🟢🟣🟡🟤⚫"
    jeux_z = np.array(game.get_game()).reshape(game.shape[0]*game.shape[1]).astype(int)
    result_array = jeux_z.copy().astype(str)
    for x in enumerate(couleurs):
        result_array = np.where(jeux_z == int(x[0]), x[1], result_array)
    result_array= result_array.reshape(game.shape[0],game.shape[1])
    result_text = ""
    for ligne in result_array:
        result_text += "".join(ligne.tolist())
        result_text +="\n"
    result_text += "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"
    if game.id_message_grille.id == 0 or new:
        game.id_message_grille = await chanel.send(result_text)
        return 1
    else:
        await game.id_message_grille.edit(content = result_text)
        return 2

async def affiche_message(game, message,chanel =None,new = False):

    boutons = ["1️⃣", "2️⃣", "3️⃣","4️⃣","5️⃣", "6️⃣","7️⃣"]
    if game == None:
        await chanel.send(message)
        return
    if game.id_message_reaction.id == 0 or new:
        game.id_message_reaction = await chanel.send(message)
        for x in boutons:
            await game.id_message_reaction.add_reaction(x)
    else:
        await game.id_message_reaction.edit(content = message)




@client.event
async def on_reaction_add(reaction, user):
    global dfGames
    if user.bot:
        #print(user, "is a bot")
        return


    message_id = reaction.message.id
    name_game = ""
    boutons = ["1️⃣", "2️⃣", "3️⃣","4️⃣","5️⃣", "6️⃣","7️⃣"]
    responce = ""

    for _, name in enumerate(games_en_cours):
        game = games_en_cours[name]
        if game.id_message_reaction.id == message_id:
            name_game = name
            break
    if len(name_game)>0:
        print(user.id,game.playersID)
        if user.id in game.playersID:
            for index,bouton in enumerate(boutons):
                if bouton == reaction.emoji:
                    responce += game.jouer(user.id, index)
                    await affiche_game(game, new = False)

                    e = game.check_winner()
                    if e[0]:
                        responce = "Gagnant <@{}> !!  \n".format(str(e[1]))
                        dfGames = dfGames.append(e[2], ignore_index = True)
                        dfGames.to_csv("data/BDD_scores.csv")
                        if supprime_game( name_game):
                            responce += "Game supprimée\n__See you later ;)__"


        else:
            await reaction.message.remove_reaction(reaction, user)
            responce += "Tu n'est malheureusement pas inscris a la partie <@{}>".format(user.id)
    if len(responce)>0:
        print(game.id_message_reaction, "id message de la game")
        await affiche_message(game = game, message=responce)

    await game.id_message_reaction.remove_reaction(reaction.emoji, user)




@client.event
async def on_message(message):
    if message.author.bot:
        return
    if len(message.content) == 2:
        return
    global games_en_cours
    split_message = message.content.split()
    mention = message.mentions
    joueur = message.author.id
    responce = " "
    repondre = True
    error = False

    if split_message[0] == "*newx4":
        # Cree une game
        name_game = split_message[1]
        nom_free = True
        try:
            games_en_cours[name_game]
            nom_free = False
            responce += "Le nom de la partie n'est pas disponible\n"
        except:
            pass

        if nom_free and len(mention) > 0:
            game = Game(mention, name = name_game)
            games_en_cours[name_game] = game
            responce += " Partie créé avec le nom de **{}**. Il y a {} joueurs \n".format(
                name_game, len(mention))
            responce += "Cliquer sur les réactions pour placé un jeton dans la column de votre choix\n **Have Fun**"
            await affiche_game(game, new = True, chanel = message.channel)
        else:
            responce += "Vous n'êtes pas assez nombreux"
            error = True

    elif split_message[0] == "*resume":
        nom_bon = True
        name_game = split_message[1]
        try:
            game = games_en_cours[name_game]
        except:
            nom_bon = False
            responce += "Le non de la partie est incorect"

        if nom_bon:
            await affiche_game(game, new = True, chanel = message.channel)
            error = True
            responce += "Welcome back <@{}>".format(message.author.id)
        else:
            error = True
    elif split_message[0] == "*destroy":
        nom_bon = True
        name_game = split_message[1]
        try:
            game = games_en_cours[name_game]
        except:
            nom_bon = False
            responce += "Le non de la partie est incorect"

        if nom_bon:
            if supprime_game( name_game):
                responce += "Game supprimée\n__See you later ;)__"
                error = True
    elif split_message[0] == "*helpx4":
        responce += "Pour demarrer une partie : \n"
        responce += "__*newx4 [nom_de_la_partie] [@joueurs1][@joueurs2][@ect]__ \n"
        responce += "Pour reprendre une partie en cours :\n"
        responce += "__*resume [nom_de_la_partie]__\n"
        responce += "Pour supprimer une partie :\n"
        responce += "__*destroy [nom_de_la_partie]__ \n"
        responce += "Have fun !"
        error = True







    else:
        repondre = False
    if repondre:
        if len(responce)> 1:
            if not error:
                await affiche_message(game,message=responce, chanel = message.channel)
            else:
                await affiche_message(chanel = message.channel, game = None, new = True, message=responce)





@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(token)
#
