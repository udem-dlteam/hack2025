# Hackathon du DIRO 2025!

   Surveillez ce fichier README car s'il y a des changements pendant le Hackathon
   nous les annoncerons ici.

## NOUVEAU!

Allez voir le fichier `LOWI_08_circuit.log` qui donne une trace d'un vol
complété correctement avec, à chaque 0.2 seconde, les valeurs de `instruments.heading`,
`instruments.roll`, `instruments.pitch`, ainsi que ce qui est envoyé vers le simulateur
pour `controls.rudder`, `controls.elevator`, `controls.aileron`, et `controls.throttle`.
Ça devrait vous donner une meilleure idée de la relation entre `instruments` et `controls`,
et l'ampleur et le signe des valeurs dans `controls`.

## Références de base

- FlightGear : https://www.flightgear.org/download/

- Moonlight : https://github.com/moonlight-stream/moonlight-qt/releases

- Fichiers `.kml` : https://earth.google.com

- Longitude/Latitude : https://en.wikipedia.org/wiki/Geographic_coordinate_system

- PID : https://www.youtube.com/watch?v=fv6dLTEvl74


## Settings de FlightGear

- Multi-player Server : `fgms.iro.umontreal.ca`

- Additional Settings : `--httpd=5400 --telnet=x,x,100,x,5454,x --allow-nasal-from-sockets`

- Download scenery automatically

- Aircraft : Cessna 172P Skyhawk (1982)

- Location : LOWI - Innsbruck Kranebitten

- Environment : Time of day "Noon", Season "Summer"


## Système de pointage

<p align="center" font-size="2em">
 <h1 align="center"><a href="https://docs.google.com/spreadsheets/d/1ohQgwI8QG8xOmhwN5UQtOV58jus0snhLu0yvMwwDQyw/edit?usp=sharing">🏆 LEADERBOARD EN TEMPS RÉEL 🏆</a></h1>
</p>


![](./Hackathon2025.png)

Toute tentative de tricherie entrainera la disqualification de l'équipe. Si vous
avez des doutes demandez aux organisateurs!

# Bienvenue au Hackaton du DIRO 2025

## Introduction

Le théme de ce hackathon est l'aviation !

Vous allez interagir programmatiquement avec un simulateur d'avion, nommé [FlightGear](https://www.flightgear.org/).

Dans un premier temps, vous allez vous approprier FlightGear, et découvrir les fonctionnalités et le réalisme offert par ce dernier !

L'équipe de préparateurs de ce hackathon a mis en place un serveur multi-joueurs, dans lequel chaque equipe aura en possession 1 joueur (avion).

Le but de ce hackathon est de résoudre le plus de défis possibles parmi ceux que nous vous proposons.

L'important est d'apprendre et de s'amuser, ne laissez pas votre esprit de compétition prendre le dessus sur votre enthousiasme !

## Préparez votre terrain de jeu

Suivez les étapes suivantes :

1. Installez [FlightGear en suivant ce lien](https://www.flightgear.org/download/)
2. Installez le client de streaming [Moonlight](https://github.com/moonlight-stream/moonlight-qt/releases)
3. Allez chercher un organisateur du hackathon, il vous donnera le mot de passe a rentrer dans **Moonlight**. Ne changez pas les paramètres de Moonlight.

NOTE: Raccourci clavier utile pour moonlight : `CTRL+SHIFT+ALT+Q` pour quitter le stream en cours + `CTRL+SHIFT+ALT+Z` pour reprendre le controle de la souris et du clavier

Pour la suite du hackathon, nous vous conseillons de développer vos programmes pour interagir avec FlightGear, avec une instance **LOCALE** de FlightGear sur votre ordinateur.

Une fois que vous pensez que vos programmes peuvent résoudre un défi (confirmé avec le programme `radar`), avertissez un organisateur que vous êtes en train de résoudre un défi sur le serveur multi-joueur.

## Initiation au pilotage

Prenez le temps de comprendre ce [document](./presentation.pdf) pour avoir un apercu de l'ensemble des propriétés physiques qui controlent la dynamique d'un avion.

Ils vous seront utiles plus tard lorsque vous allez comprendre l'ensemble des propriétés que FLightGear vous expose !

## Jouez à FlightGear

Avant d'interagir avec FlightGear à tavers du code, prenez le temps de connaitre un peu plus le jeu !

Nous vous conseillons de jouer avec toutes les sections du menu `Help`, notamment retenez les raccourcis claviers les plus importants! Hesitez pas aussi à faire aussi quelques tutorials, ils sont tres rapides et très bien faits !

## Contrôler un avion via du code

FlightGear donne la possibilité d'interagir avec son interface avec du code.

Le simulateur possède des flags qui peuvent être activés, au moment de son lancement.

Les flags qui seront d'intérêt pour vous, dans ce hackathon, sont les suivants:

* `--httpd=5400`
* `--telnet=x,x,100,x,5454,x`
* `--allow-nasal-from-sockets`

L'état de FlightGear peut etre consulté via le [**PropertyTree**](https://wiki.flightgear.org/Property_Tree/Explained)

Ce [dépôt](https://github.com/julianneswinoga/flightgear-python/blob/master/flightgear_python) fournit de bons wrappers Python pour interagir avec FlightGear ! !!


## Connexion à FlightGear via code
* Installer [Chisel](https://github.com/jpillora/chisel/releases/tag/v1.10.1)
* Exécutez la commande suivante pour vous connecter a FlightGear :
```bash
chisel client -auth "<user>:<pass>" blgXX.iro.umontreal.ca:8000 127.0.0.1:5501:127.0.0.1:5501/udp 127.0.0.1:5503:127.0.0.1:5503/udp 127.0.0.1:5454:127.0.0.1:5454/tcp 127.0.0.1:8080:127.0.0.1:8080 R:127.0.0.1:5502:127.0.0.1:5502/udp R:127.0.0.1:5504:127.0.0.1:5504/udp
```
* Exécutez la commande suivante pour vérifier
```bash
python modules/FG_example.py
```
