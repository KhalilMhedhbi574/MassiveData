#!/usr/bin/env python3
import csv
import os
import random
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

# ================== CONFIG GLOBALE ==================

BASE_URL = "https://tinyinsta-478213.ew.r.appspot.com"
TIMELINE_PATH = "/api/timeline"        
TIMELINE_LIMIT = 20

NB_USERS_TOTAL = 1000
POSTS_PER_USER = 50
FOLLOWEES_PER_USER = 20

CONCURRENCY_LEVELS = [1, 10, 20, 50, 100, 1000]
NB_RUNS = 3

OUT_FILE = "/home/khalilfahler/out/conc.csv"
USER_PREFIX = "user"

# ================== FONCTIONS UTILITAIRES ==================


def make_username(i: int) -> str:
    return f"{USER_PREFIX}{i}" 


def timeline_url(username: str) -> str:
    return f"{BASE_URL}{TIMELINE_PATH}?user={username}&limit={TIMELINE_LIMIT}"


def fetch_timeline(username: str, timeout: float = 10.0) -> float:
    # Envoie une requête GET sur la timeline d'un user.
    # Retourne la durée en millisecondes.
    url = timeline_url(username)
    start = time.perf_counter()
    resp = requests.get(url, timeout=timeout)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code} for {url}")
    return elapsed_ms


def run_parallel_timeline(usernames, max_workers: int) -> tuple[float, int]:
    # Exécute des timelines en parallèle pour une liste d'usernames.
    # Retourne (avg_time_ms, failed_flag).
    times = []
    failed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_timeline, u): u for u in usernames
        }
        for fut in as_completed(futures):
            user = futures[fut]
            try:
                t = fut.result()
                times.append(t)
            except Exception as e:
                print(f"[ERR] timeline {user}: {e}")
                failed = 1

    avg_ms = sum(times) / len(times) if times else 0.0
    return avg_ms, failed


def pick_usernames(n: int):
    # Choisit n usernames distincts parmi user1..userNB_USERS_TOTAL.
    indices = random.sample(range(1, NB_USERS_TOTAL + 1), n)
    return [make_username(i) for i in indices]


# ================== COLD START, SEED & MAIN ==================
def cold_start(repeats: int = 5):
    #Effectue quelques appels de warmup pour amortir le cold start.
    warm_user = pick_usernames(repeats)
    print(f"[COLDSTART] warmup {repeats} rêquetes")    
    for i in range(repeats):
        url = timeline_url(warm_user[i])
        try:
            requests.get(url, timeout=10.0)
        except Exception as e:
            print(f"[COLDSTART] erreur ignorée: {e}")
    print(f"[COLDSTART] Terminé")

def delete_all_data():
    # Appelle delete_data.py pour supprimer tous les Users / Posts / etc.
    print("[INIT] Suppression complète des données (delete_data.py)")
    subprocess.check_call(["python", "/home/khalilfahler/scripts/tools/delete_data.py"])


def seed_full_dataset():
    # Seed une seule fois :
    #   - 1000 users
    #   - ~50 posts par user
    #   - ~20 followees par user
    total_posts = NB_USERS_TOTAL * POSTS_PER_USER
    print(
        f"[SEED] users={NB_USERS_TOTAL}, total_posts={total_posts}, "
        f"followees≈{FOLLOWEES_PER_USER}"
    )

    cmd = [
        "python",
        "/home/khalilfahler/massive-gcp/seed.py",
        "--users",
        str(NB_USERS_TOTAL),
        "--posts",
        str(total_posts),
        "--follows-min",
        str(FOLLOWEES_PER_USER),
        "--follows-max",
        str(FOLLOWEES_PER_USER),
        "--prefix",
        USER_PREFIX,
    ]
    subprocess.check_call(cmd)


def main():
    # Préparation du datastore
    delete_all_data()
    seed_full_dataset()
    # Bench & CSV
    print(f"[BENCH] Résultats → {OUT_FILE}")
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["PARAM", "AVG_TIME", "RUN", "FAILED"])

        for conc in CONCURRENCY_LEVELS:
            print(f"\n=== CONCURRENCY PARAM={conc} ===")
            # Bench (3 runs)
            for run_id in range(1, NB_RUNS + 1):
                usernames = pick_usernames(conc)
                cold_start()
                avg_ms, failed = run_parallel_timeline(
                    usernames, max_workers=conc
                )
                print(f"Run {run_id}: avg={avg_ms:.2f} ms, failed={failed}")
                # Écriture du CSV
                writer.writerow(
                    [conc, f"{avg_ms:.2f}ms", run_id, failed]
                )
    print(f"[BENCH FINALISE] Résultats → {OUT_FILE}")


if __name__ == "__main__":
    main()
