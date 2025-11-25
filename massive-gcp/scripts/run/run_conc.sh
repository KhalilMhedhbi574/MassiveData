#!/bin/bash
# Benchmark de concurrence -> massive-gcp/out/conc.csv

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

# --- Compute ROOT_DIR and OUT_DIR correctly ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUT_DIR="$ROOT_DIR/out"

mkdir -p "$OUT_DIR"

CSV="$OUT_DIR/conc.csv"
BASE_URL="https://tinyinsta-478213.ew.r.appspot.com/api/timeline"
USER="conc-1"  # utilisateur de test

echo "PARAM,AVG_TIME,RUN,FAILED" > "$CSV"

TOTAL_REQ=1000

for c in 1 10 20 50 100 1000; do
  for run in 1 2 3; do
    echo ">>> Concurrency=${c}, run=${run}"

    RESULT=$(ab -n $TOTAL_REQ -c $c "${BASE_URL}?user=${USER}&limit=20" 2>&1)

    # extraction propre du temps
    TIME=$(echo "$RESULT" | grep "Time per request" | head -n 1 | awk '{print $4}')
    FAILED=0

    if [ -z "$TIME" ]; then
      TIME="NA"
      FAILED=1
      echo "  -> Impossible d'extraire le temps moyen, marqué FAILED=1"
    else
      TIME="${TIME}ms"
    fi

    echo "${c},${TIME},${run},${FAILED}" >> "$CSV"
  done
done

echo "✅ Benchmark conc terminé."
echo "➡️ Résultats : $CSV"
