#!/bin/bash
set -euo pipefail

echo " Wipe complet du Datastore..."
python3 "/home/khalilfahler/scripts/tools/delete_data.py"

cd "/home/khalilfahler/massive-gcp"

echo " Seed pour l'expérience POSTS (10, 100, 1000 posts/user, 20 followees)..."

# 10 posts par user (en moyenne)
python3 seed.py \
  --users 1000 \
  --posts 10000 \
  --follows-min 20 \
  --follows-max 20 \
  --prefix post10-

# 100 posts par user (en moyenne)
python3 seed.py \
  --users 1000 \
  --posts 100000 \
  --follows-min 20 \
  --follows-max 20 \
  --prefix post100-

# 1000 posts par user (en moyenne) 
python3 seed.py \
  --users 1000 \
  --posts 1000000 \
  --follows-min 20 \
  --follows-max 20 \
  --prefix post1000-

echo "✅ Seed POSTS terminé."
echo "   Utilisateurs de test pour run_post.sh : post10-1, post100-1, post1000-1"
