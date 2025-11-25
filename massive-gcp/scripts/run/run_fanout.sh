#!/bin/bash
# Benchmark fanout -> massive-gcp/out/fanout.csv

set -euo pipefail

# --- Check ApacheBench (ab) and install if missing ---
if ! command -v ab >/dev/null 2>&1; then
    echo "⚠️  ApacheBench (ab) n'est pas installé. Installation..."
    sudo apt-get update -y && sudo apt-get install -y apache2-utils
    if ! command -v ab >/dev/null 2>&1; then
        echo "❌ Impossible d'installer ab. Arrêt du script."
        exit 1
    fi
    echo "✅ ApacheBench installé avec succès."
else
    echo "✅ ApacheBench (ab) est déjà installé."
fi

# Répertoire où se trouve ce script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Répertoire racine du projet (massive-gcp)
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Répertoire out/ au niveau de massive-gcp
OUT_DIR="$ROOT_DIR/out"
mkdir -p "$OUT_DIR"

CSV="$OUT_DIR/fanout.csv"

BASE_URL="https://tinyinsta-478213.ew.r.appspot.com/api/timeline"
CONC=50
TOTAL_REQ=1000

echo "PARAM,AVG_TIME,RUN,FAILED" > "$CSV"

for FAN in 10 50 100; do
  PREFIX="fan${FAN}-"
  USER="${PREFIX}1"

  echo "=== BENCH fanout=${FAN}, user=${USER} ==="

  for RUN in 1 2 3; do
    echo ">>> FANOUT=${FAN}, RUN=${RUN}"

    RESULT=$(ab -n "$TOTAL_REQ" -c "$CONC" \
      "${BASE_URL}?user=${USER}&limit=20" 2>&1)

    TIME=$(echo "$RESULT" | grep "Time per request" | head -n 1 | awk '{print $4}')
    FAILED=0

    if [ -z "$TIME" ]; then
      TIME="NA"
      FAILED=1
      echo "  -> Impossible d'extraire le temps moyen, marqué FAILED=1"
    fi

    echo "${FAN},${TIME},${RUN},${FAILED}" >> "$CSV"
  done
done

echo "✅ Benchmark fanout terminé."
echo "➡️ Résultats : $CSV"
