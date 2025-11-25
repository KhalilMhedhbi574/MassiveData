#!/bin/bash
set -euo pipefail

echo " Wipe complet du Datastore..."
python3 "/home/khalilfahler/scripts/tools/delete_data.py"

cd "/home/khalilfahler/massive-gcp"

echo " Seed pour l'expérience FANOUT (100 posts/user, fanout = 10, 50, 100)..."

# fanout = 10 followees
python3 seed.py \
  --users 1000 \
  --posts 100000 \
  --follows-min 10 \
  --follows-max 10 \
  --prefix fan10-

# fanout = 50 followees
python3 seed.py \
  --users 1000 \
  --posts 100000 \
  --follows-min 50 \
  --follows-max 50 \
  --prefix fan50-

# fanout = 100 followees
python3 seed.py \
  --users 1000 \
  --posts 100000 \
  --follows-min 100 \
  --follows-max 100 \
  --prefix fan100-

echo "✅ Seed FANOUT terminé."
echo "   Utilisateurs de test pour run_fanout.sh : fan10-1, fan50-1, fan100-1"
