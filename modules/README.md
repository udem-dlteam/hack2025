# modules

Ce dossier contient plusieurs modules utiles pour contrôler le simulateur et
faire de la navigation.

## Module `FG.py`

Module d'interface à FlightGear qui utile l'interface "telnet". Les fonctions de
ce module sont illustrées dans le programme `FG_example.py`.

## `python3 FG_example.py`

Démarre le moteur du Cessna 172 et fait un décollage en actionnant les contrôles
de l'avion. C'est un très mauvais décollage (qui vire à gauche) mais au moins on
a quitté le sol des vaches pendant un instant!

Avant d'exécuter ce programme, assurez-vous d'avoir placé votre avion à l'aéroport
LOWI sur la piste 08 (sur d'autres aéroports le décollage risque d'être moins bien
réussi!).

## Module `geodetic.py`

Fait des calcul de position sur la terre. Une position est représentée
par la classe `Location` qui contient le trio latitude/longitude/altitude.
Des fonctions de ce module permettent de calculer la distance entre deux `Location`
ainsi que la direction (bearing) d'un `Location` par rapport à une autre `Location`.
N'hésitez pas à explorer le code de ce module pour découvrir d'autres fonctions.

## Module `airports.py`

Donne des informations sur les pistes des aéroports (le nom des pistes, leur position,
leur direction, etc).

## Programme `parcours_gen.py`

Programme qui a été utilisé pour créer les parcours du Hackathon.
