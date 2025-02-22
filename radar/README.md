# radar

Le programme `radar` permet de visionner la position des avions sur une carte et
de vérifier que l'avion a correctement complété un parcours sans jamais s'éloigner au
delà de la zone de tolérance du parcours. Si le message `[OFF-COURSE]` s'affiche
votre avion devra recommencer le parcours du début!

## `python3 radar/radar.py`

Démarre un navigateur web qui affiche la carte autour de Innsbruck et les avions
qui se trouvent dans cette zone.

## `python3 radar/radar.py LOWI_08_circuit`

Le parcours `LOWI_08_circuit` sera affiché sur la carte. Le programme va vérifier que ce
parcours est correctement suivi par les avions.
Attention... la carte ne s'étend pas jusqu'à l'aéroport de LOIJ, mais les vérifications
du parcours sont quand même effectuées correctement.

## `python3 radar/radar.py parcours.csv`

Fait la vérification avec un parcours spécifique défini par un fichier `.csv`.

## `python3 radar/radar.py --mps`

Affiche les tous les avions pris en charge par le "Multi-Player Server" du Hackathon.

## `python3 radar/radar.py une.addresse.internet:5400`

Affiche l'avion qui est simulé par FlightGear sur la machine `une.addresse.internet`.
