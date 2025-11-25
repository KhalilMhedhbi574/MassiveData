#!/bin/bash
# Benchmark taille des données (nb de posts par user) -> massive-gcp/out/post.csv

set -euo pipefail

# --- Check ApacheBench (ab) and install if missing ---
if ! command -v ab >/dev/null 2>&1; then
    echo "  ApacheBench (ab) n'est pas installé. Installation..."
    sudo apt-get update -y && sudo apt-get install -y apache2-utils
    if ! command -v ab >/dev/null 2>&1; then
        echo " Impossible d'installer ab. Arrêt du script."
        exit 1
    fi
    echo "✅ ApacheBench installé avec succès."
else
    echo "✅ ApacheBench (ab) est déjà installé."
fi

OUT_DIR="/home/khalilfahler/out"
mkdir -p "$OUT_DIR"

CSV="$OUT_DIR/post.csv"

# URL de l'appli déployée
BASE_URL="https://tinyinsta-478213.ew.r.appspot.com/api/timeline"

# Concurrence fixée à 50 
CONC=50

# Nombre total de requêtes par run
TOTAL_REQ=1000

echo "Écriture dans $CSV"
echo "PARAM,AVG_TIME,RUN,FAILED" > "$CSV"

# Pour chaque nombre de posts par user : 10, 100, 1000
for POSTS_PER_USER in 10 100 1000; do
  PREFIX="post${POSTS_PER_USER}-"

  # Utilisateur de test pour ce dataset 
  USER="${PREFIX}1"

  echo "=== BENCH posts_per_user=${POSTS_PER_USER}, user=${USER} ==="

  # 3 runs par configuration
  for RUN in 1 2 3; do
    echo ">>> POSTS_PER_USER=${POSTS_PER_USER}, RUN=${RUN}"

    RESULT=$(ab -n "$TOTAL_REQ" -c "$CONC" \
      "${BASE_URL}?user=${USER}&limit=20" 2>&1)

    TIME=$(echo "$RESULT" | grep "Time per request" | head -n 1 | awk '{print $4}')
    FAILED=0

    if [ -z "$TIME" ]; then
      TIME="NA"
      FAILED=1
      echo "  -> Impossible d'extraire le temps moyen, marqué FAILED=1"
    else
      TIME="${TIME}ms"
    fi

    echo "${POSTS_PER_USER},${TIME},${RUN},${FAILED}" >> "$CSV"
  done
done

echo "✅ Benchmark post terminé."
echo "➡️ Résultats : $CSV"
