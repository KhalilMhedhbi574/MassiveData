#!/usr/bin/env python3
"""Script de peuplement (seed) pour Tiny Instagram.

Usage basique:
  python seed.py --users 5 --posts 40 --follows-min 1 --follows-max 3

Paramètres:
  --users        Nombre d'utilisateurs à créer (user1 .. userN)
  --posts        Nombre total de posts à répartir
  --follows-min  Nombre minimum de follows par utilisateur
  --follows-max  Nombre maximum de follows par utilisateur
  --prefix       Préfixe des noms d'utilisateurs (default: user)
  --dry-run      N'écrit rien, affiche seulement le plan

Le script est idempotent sur les utilisateurs (il ne recrée pas si existants) et ajoute simplement des posts supplémentaires.

ATTENTION: Ce script écrit directement dans Datastore du projet courant (gcloud config get-value project).

Paramètres ajoutés:
  --skip-follows  Saute l'étape d'ajustement des relations de suivi.
  --skip-posts    Saute l'étape de création de nouveaux posts. 

RÈGLE D'EFFICACITÉ AJOUTÉE : Si --skip-follows est utilisé, l'étape de vérification/création des utilisateurs est aussi sautée automatiquement pour économiser les lectures Datastore.
"""
from __future__ import annotations
import argparse
import random
from datetime import datetime, timedelta
from google.cloud import datastore


def parse_args():
    p = argparse.ArgumentParser(description="Seed Datastore for Tiny Instagram")
    p.add_argument('--users', type=int, default=5, help="Nombre d'utilisateurs à cibler/créer.")
    p.add_argument('--posts', type=int, default=30, help="Nombre total de posts à créer.")
    p.add_argument('--follows-min', type=int, default=1, help="Min de follows par utilisateur.")
    p.add_argument('--follows-max', type=int, default=3, help="Max de follows par utilisateur.")
    p.add_argument('--prefix', type=str, default='user', help="Préfixe des noms d'utilisateurs.")
    p.add_argument('--dry-run', action='store_true', help="Affiche le plan sans écrire dans Datastore.")
    
    # Arguments ajoutés
    p.add_argument('--skip-follows', action='store_true', help="Saute l'étape d'ajustement des relations de suivi.")
    p.add_argument('--skip-posts', action='store_true', help="Saute l'étape de création de posts.")
    
    return p.parse_args()


def ensure_users(client: datastore.Client, names: list[str], dry: bool):
    created = 0
    for name in names:
        key = client.key('User', name)
        entity = client.get(key)
        if entity is None:
            entity = datastore.Entity(key)
            entity['follows'] = []
            if not dry:
                client.put(entity)
            created += 1
    return created

# Fonction modifié pour rajouter les users après assignation des follows par 500
def assign_follows(client: datastore.Client, names: list[str], fmin: int, fmax: int, dry: bool):
    batch = None
    batch_count = 0   # nb d'entités dans le batch courant
    total_puts = 0    # nb total d'entités mises à jour

    for name in names:
        # Créer un batch si besoin
        if batch is None and not dry:
            batch = client.batch()
            batch.begin()

        key = client.key('User', name)
        entity = client.get(key)
        if entity is None:
            continue # devrait exister
        # Générer un set de follows (exclure soi-même)
        others = [u for u in names if u != name]
        if not others:
            continue
        target_count = random.randint(min(fmin, len(others)), min(fmax, len(others)))
        selection = random.sample(others, target_count)
        # Fusion avec existants
        existing = set(entity.get('follows', []))
        new_set = sorted(existing.union(selection))
        entity['follows'] = new_set

        if not dry:
            batch.put(entity)
            batch_count += 1
            total_puts += 1

            if batch_count >= 500:
                batch.commit()
                print(f"**[Seed] Batch de follows commit. Total cumulé : {total_puts}**")
                batch = None
                batch_count = 0

    # Commit du dernier batch partiel
    if batch is not None and batch_count > 0 and not dry:
        batch.commit()
        print(f"**[Seed] Dernier batch de follows commit. Total cumulé : {total_puts}**")


# Fonction modifié pour rajouter les posts par 500
def create_posts(client: datastore.Client, names: list[str], total_posts: int, dry: bool):
    if not names or total_posts <= 0:
        return 0
    created = 0
    cpt=0
    # Répartition simple: choix aléatoire d'auteur pour chaque post
    base_time = datetime.utcnow()
    for i in range(total_posts):
        if cpt==0:
            batch=client.batch()
            batch.begin()
        cpt+=1
        author = random.choice(names)
        key = client.key('Post')
        post = datastore.Entity(key)
        # Décaler artificiellement le timestamp pour obtenir un tri naturel
        post['author'] = author
        post['content'] = f"Seed post {i+1} by {author}"
        post['created'] = base_time - timedelta(seconds=i)
        if not dry:
            batch.put(post)
        created += 1
        if cpt==500:
            batch.commit()
            cpt=0
            print(f"**[Seed] Posts créés: {created}**")
          # Commit du dernier batch partiel
    if batch is not None and cpt > 0 and not dry:
        batch.commit()
        print(f"**[Seed] Dernier batch de posts commit. Total cumulé : {created}**")
    return created

def main():
    args = parse_args()
    client = datastore.Client()

    user_names = [f"{args.prefix}{i}" for i in range(1, args.users + 1)]
    
    # ----------------------------------------------------
    # NOUVELLE LOGIQUE POUR LE SKIP DES UTILISATEURS
    # ----------------------------------------------------
    # On saute l'étape des utilisateurs si l'utilisateur a demandé de sauter les follows 
    # (--skip-follows) ou les posts (--skip-posts), impliquant qu'il suppose que les utilisateurs 
    # existent déjà.
    skip_user_step = args.skip_posts or args.skip_follows
    
    if not skip_user_step:
        print(f"**[Seed] Utilisateurs ciblés: {user_names}**")
    else:        
        reason = ""
        if args.skip_posts:
            reason += " (--skip-posts activé)"
        if args.skip_follows:
            reason += " (--skip-follows activé)" 
        print(f"**[Seed] Skip: Vérification/Création des utilisateurs**{reason}")
    if args.dry_run:
        print("[Dry-Run] Aucune écriture ne sera effectuée.")

    print("-" * 30)

    # 1. Users (Conditionnel)
    if not skip_user_step:
        print("**[Seed] Exécution: Vérification/Création des Utilisateurs**")
        new_users = ensure_users(client, user_names, args.dry_run)
        print(f"**[Seed] Nouveaux utilisateurs créés: {new_users}**")

        
    print("-" * 30)

    # 2. Follows (Conditionnel)
    if not args.skip_follows:
        print(f"**[Seed] Exécution: Relations de suivi** (Min: {args.follows_min}, Max: {args.follows_max})")
        assign_follows(client, user_names, args.follows_min, args.follows_max, args.dry_run)
        print("[Seed] Relations de suivi ajustées.")
    else:
        print("**[Seed] Skip: Relations de suivi** (--skip-follows activé)")
        
    print("-" * 30)

    # 3. Posts (Conditionnel)
    if not args.skip_posts:
        print(f"**[Seed] Exécution: Création de Posts** (Total: {args.posts})")
        created_posts = create_posts(client, user_names, args.posts, args.dry_run)
        print(f"**[Seed] Posts créés: {created_posts}**")
    else:
        print("**[Seed] Skip: Création de Posts** (--skip-posts activé)")

    print("-" * 30)
    print("**[Seed] Terminé.**")


if __name__ == '__main__':
    main()
