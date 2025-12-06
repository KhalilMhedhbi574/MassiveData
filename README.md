# Massive Data  
Projet réalisé par **Khalil Mhedhbi M1 ATAL** 

##  Objectif du projet

Le projet **Massive Data** vise à étudier comment les performances de l’application **TinyInsta** évoluent selon trois axes principaux :

- La **concurrence** (nombre d’utilisateurs simultanés)  
- La **taille des données** (nombre de posts par utilisateur)  
- Le **fanout** (nombre de followees par utilisateur)  

L’application TinyInsta, fournie par l’enseignant, expose une API `/api/timeline` permettant de récupérer la timeline d’un utilisateur.  
Pour chaque configuration testée, nous mesurons le **temps moyen d’exécution** (en millisecondes) d’une requête à l’API, en répétant chaque mesure **3 fois**.

Toutes les expérimentations sont réalisées avec **Python**.

---

## Webapp déployée

L’application TinyInsta est déployée à l’adresse suivante :  
https://tinyinsta-478213.ew.r.appspot.com

---

## Structure du dépôt

```
MassiveData/
├── massive-gcp/
│   └── (sources TinyInsta)
│
├── out/
│   ├── conc.csv
│   ├── post.csv
│   ├── fanout.csv
│   ├── conc.png
│   ├── post.png
│   └── fanout.png
│
├── scripts/
│   ├── bench/
│   │   ├── bench_conc.py
│   │   ├── bench_post.py
│   │   └── bench_fanout.py
│   ├── plot/
│   │   ├── plot_conc.py
│   │   ├── plot_post.py
│   │   └── plot_fanout.py
│   └── tools/
│       └── delete_data.py
```

---

## Génération des données (Seed)

Avant chaque série d’expérimentations, les données du Datastore sont **vidées**, puis remplis.

Le script principal `seed.py` a été **modifié** :

- Ajout de **flags** comme `--skip-follows` pour sauter certaines étapes (posts, followees, etc.) afin de ne pas avoir a réimporter toutes la base à chaque changement de paramètre.  
- **Batching** des requêtes (insertion par lots) pour posts et followees pour accélerer considérablement la vitesse de l'insertion (un million de posts en 15 minutes).  

## Benchmarks  

- **Concurrence** — 1000 users, 50 posts/user, 20 followees  
  ```bash
  /scripts/bench/bench_conc.py
  ```  

- **Taille des données (posts)** — posts = 10, 100, 1000  
  ```bash
  /scripts/bench/bench_post.py
  ```  

- **Fanout (followees)** — followees = 10, 50, 100  
  ```bash
  /scripts/bench/bench_fan.py
  ```

Chaque script :  
- lance les requêtes sur des utilisateurs distincts en parallèle grâce à des threads,  
- lance **3 runs par paramètre** avec un **cold start** avant chaque run,
- met à jour les paramètres (notamment grâce à --skip-follows et skip--posts de seed.py)  
- génère un fichier CSV conforme,  
- écrit le résultat dans `out/*.csv`.

---

## Graphiques (barplots)

Les scripts de génération de graphiques se trouvent dans `scripts/plot/*.py`. Ils lisent les CSV résultants et produisent des PNG dans `out/` :

- **Concurrence** → `conc.png`  
- **Taille des données (posts)** → `post.png`  
- **Fanout** → `fanout.png`  

---

## Analyse synthétique des résultats

### Concurrence  

Le temps de réponse augmente progressivement mais moins que linéairement avec le nombre d’utilisateurs concurrents.  
On observe une augmentation exponentielle avec 1000 cependant.

![Graphique Conc](/out/conc.png)

### Taille des données (posts par user)  

Le passage de 10 à 100 posts par user n'a presque pas changé les resultats hormis la variance. 
Le passage à 1000 posts par user, quant à lui, double presque le temps tout en restant sous la seconde. 

![Graphique Conc](/out/post.png)

### Fanout (nombre de followees)  

On observe une augmentation presque linéaire pour fanout. On se situe autour de la seconde pour 10 followees, 5 secondes pour 50 followees et 10 secondes pour 100 followees. C'est le bench le plus couteux en temps.

![Graphique Conc](/out/fanout.png)

---

## Cloner le dépôt

```bash
git clone https://github.com/KhalilMhedhbi574/MassiveData.git
cd MassiveData
```

## Lancer un benchmark

```bash
  python /scripts/bench/bench_conc.py
# ou bench_post.py, bench_fanout.py selon l’expérience souhaitée
```

## Générer les graphiques

```bash
python scripts/plot/plot_conc.py
# idem pour post / fanout
```

---

## Liens de rendu (Madoc)

- **GitHub** : https://github.com/KhalilMhedhbi574/MassiveData  
- **Application TinyInsta déployée** : https://tinyinsta-478213.ew.r.appspot.com
