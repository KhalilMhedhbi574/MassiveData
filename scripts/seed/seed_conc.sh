#!/bin/bash
set -euo pipefail

echo " Wipe complet du Datastore..."
python3 "/home/khalilfahler/scripts/tools/delete_data.py"

cd "/home/khalilfahler/massive-gcp"

echo " Seed pour l'expérience CONCURRENCE (1000 users, 50 posts/user, 20 followees)..."

python3 seed.py \
  --users 1000 \
  --posts 50000 \
  --follows-min 20 \
  --follows-max 20 \
  --prefix conc-


echo "✅ Seed CONC terminé."
echo "   Utilisateur de test pour run_conc.sh : conc-1"
