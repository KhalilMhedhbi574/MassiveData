# Massive Data  
Projet réalisé par **Khalil Mhedhbi**

##  Objectif du projet

Le but de ce projet est d’étudier comment les performances de l’application **TinyInsta** évoluent en fonction :

1. **de la concurrence (nombre d’utilisateurs simultanés)**  
2. **de la taille des données (nombre de posts par utilisateur)**  
3. **du fanout (nombre de followees par utilisateur)**  

L’application TinyInsta, fournie par l’enseignant, expose une API `/api/timeline` permettant de récupérer la timeline d’un utilisateur.  
Nous mesurons le **temps moyen d’exécution (ms)** d’une requête, en répétant chaque mesure **3 fois**.

Toutes les expérimentations sont réalisées via **ApacheBench (ab)**.

---

##  Webapp déployée

https://tinyinsta-478213.ew.r.appspot.com

---

##  Structure du repository

MassiveData/  
├── out/  
│ ├── conc.csv  
│ ├── post.csv  
│ ├── fanout.csv  
│ ├── conc.png  
│ ├── post.png  
│ └── fanout.png  
│  
├── scripts/  
│ ├── bench/  
│ │ ├── run_conc.sh  
│ │ ├── run_post.sh  
│ │ └── run_fanout.sh  
│ ├── seed/  
│ │ ├── seed_conc.sh  
│ │ ├── seed_post.sh  
│ │ └── seed_fan.sh  
│ ├── plot/  
│ │ ├── plot_conc.py  
│ │ ├── plot_post.py  
│ │ └── plot_fanout.py  
│ └── tools/
│   └── wipe_datastore.py  
└── massive-gcp/  
    └── (sources TinyInsta)

---

#  Génération des données (Seed)

Pour chaque expérience, les données du Datastore sont **entièrement vidées**, puis regénérées via un script `seed_X.sh`.

###  1) Concurrence — 1000 users, 50 posts/user, 20 followees  
```
./scripts/seed/seed_conc.sh
```

###  2) Taille des données — posts = 10, 100, 1000  
```
./scripts/seed/seed_post.sh
```

###  3) Fanout — followees = 10, 50, 100  
```
./scripts/seed/seed_fan.sh
```

---

#  Benchmarks

Les scripts suivants exécutent ApacheBench et produisent les CSV finaux :

- **Concurrence** :  
  `./scripts/bench/run_conc.sh`

- **Taille des données (posts)** :  
  `./scripts/bench/run_post.sh`

- **Fanout** :  
  `./scripts/bench/run_fanout.sh`

Chaque script :  
✔ installe `ab` automatiquement si absent  
✔ lance 3 runs par paramètre  
✔ génère un fichier CSV conforme au sujet  
✔ écrit dans `out/*.csv`

---

#  Graphiques (barplots)

Les plots se trouvent dans `scripts/plot/*.py` et génèrent automatiquement les PNG dans `out/`.

##  1. Concurrence — `conc.png`
(voir GitHub)

##  2. Taille des données — `post.png`
(voir GitHub)

##  3. Fanout — `fanout.png`
(voir GitHub)

---

#  Analyse synthétique

###  Concurrence  
Le temps de réponse augmente très nettement à partir de 100 utilisateurs concurrents, et explose à 1000.

###  Taille des données  
10 → 100 posts/user : faible impact  
1000 posts/user : forte dégradation  

###  Fanout  
Plus le nombre de followees augmente, plus la timeline est longue à construire.

---

#  Liens de rendu (Madoc)

- **GitHub :** https://github.com/KhalilMhedhbi574/MassiveData
- **Application TinyInsta déployée :** https://tinyinsta-478213.ew.r.appspot.com







timeline sur users distints paralleles
coldstart
reseed a chaque fois ou incrémenter
utiliser subprocess pour paralleles et inverser boucle for
