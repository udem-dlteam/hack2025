# Hackathon du DIRO 2025!

   Surveillez ce fichier README car s'il y a des changements pendant le Hackathon
   nous les annoncerons ici.


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
# Bienvenue au Hackaton du DIRO 2025 
Hackathon 2025 du DIRO (Département d'Informatique et de Recherche Opérationnelle) !

![](./Hackathon2025.png)

Toute tentative de tricherie entrainera la disqualification de l'équipe. Si vous
avez des doutes demandez aux organisateurs!


## Introduction

Le théme de ce hackathon est l'aviation !

Vous allez interagir programmatiquement avec un simulateur d'avion, nommé [FlightGear](https://www.flightgear.org/).

Dans un premier temps, vous allez vous approprier FlightGear, et découvrir les fonctionnalités et le réalisme offert par ce dernier !

L'équipe de préparateurs de ce hackathon a mis en place un serveur multi-joueurs, dans lequel chaque equipe aura en possession 2 joueurs (avions).

Le but de ce hackathon est de resoudre le plus de challenges possibles parmi ceux que nous vous proposons. 

L'important est d'apprendre et de s'amuser, ne laissez pas votre esprit de compétition prendre le dessus sur votre enthousiasme !

## Préparez votre terrain de jeu

Suivez les étapes suivants:

1. Installez [FlightGear en suivant ce lien](https://www.flightgear.org/download/)
2. Installez le client de streaming [Moonlight](https://github.com/moonlight-stream/moonlight-qt/releases)
3. Allez chercher un organisateur du hackathon, il vous donnera le mot de passe a rentrer dans **Moonlight**. Ne changez pas les paramètres de Moonlight.

NOTE: Raccourci clavier utile pour moonlight : `CTRL+SHIFT+ALT+Q` pour quitter le stream en cours + `CTRL+SHIFT+ALT+Z` pour reprendre le controle de la souris et du clavier 

Pour la suite du hackathon, nous vous conseillons de développer vos programmes pour interagir avec FlightGear, avec une instance **LOCAL** de FlightGear.

Une fois que vous pensez que vos programmes peuvent résoudre un challenge, avertir un organisateur que vous êtes en train de résoudre un challenge sur le serveur multi-joueur.

## Initiation au pilotage

Prenez le temps de comprendre de lire ce [document](./bases-pilotage.pdf) pour avoir un apercu de l'ensemble des propriétés physiques qui controlent la dynamique d'un avion.

Ils vous seront utiles plus tard lorsque vous allez comprendre l'ensemble des propriétés que FLightGear vous expose !

## Jouez à FlightGear

Avant d'interagir avec FlightGear à tavers du code, prenez le temps de connaitre un peu plus le jeu ! 

Nous vous conseillons de jouer avec toutes les sections du menu `Help`, notamment retenez les raccourcis claviers les plus importants! Hesitez pas aussi à faire aussi quelques tutorials, ils sont tres rapides et très bien faits !

## Controler un avion via du code

FlightGear donne la possibilité d'interagir avec son interface avec du code.

Le simulateur possède des flags qui peuvent être activés, au moment de son lancement.

Les flags qui seront d'intérêt pour vous, dans ce hackathon, sont les suivants:

* `--native-fdm`
* `--native-ctrls`

FlightGear peut etre modifiée via le [**PropertyTree**](https://wiki.flightgear.org/Property_Tree/Explained)

Ce [dépôt](https://github.com/julianneswinoga/flightgear-python/blob/master/flightgear_python) fournit de bons wrappers Python pour interagir avec FlightGear ! !!

FlightGear peut exposer 5 interfaces réseaux, en supposant une instance de FlightGear correctement configurée et active, avec lesquelles nous pouvons interagir :

* Interfaces à travers lesquelles nous ne pouvons pas contrôler directement le PropertyTree (seulement **un sous-ensemble** de propriétés spécifiques) :

    * Pour interagir avec le protocole [FDM (Flight Dynamic Model)](https://wiki.flightgear.org/Flightgear_FDM_properties) , en ajoutant ces flags --native-fdm=socket,out,30,localhost,5501,udp --native-fdm=socket,in,30,localhost,5502,udp, nous disposons d'un canal reseau pour contrôler FDM.

    * Pour contrôler le protocole [FG Native Controls](https://github.com/julianneswinoga/flightgear-python/blob/master/flightgear_python/ctrls_v27.py) : --native-ctrls=socket,out,30,localhost,5503,udp --native-ctrls=socket,in,30,localhost,5504,udp

    * **(Pas utile pour ce hackathon)** Pour contrôler le protocole de l'interface graphique native de FG : --native-gui=socket,out,30,localhost,5505,udp --native-gui=socket,in,30,localhost,5506,udp

*  **(Pas utile pour ce hackathon)** ici nous pouvons tout modifier en interagissant directement avec le PropertyTree :

    * **(Pas utile pour ce hackathon)** Via un deamon HTTP, --httpd=8080

    * **(Pas utile pour ce hackathon)** Via le protocole telnet, --telnet=socket,bi,30,localhost,5500,tcp, pour envoyer  du code [nasal](https://wiki.flightgear.org/Nasal_scripting_language).

Ces interfaces constituent donc l'entière marge de manoeuvre pour modifier Flightgear.
