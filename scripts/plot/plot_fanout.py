#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt

# Répertoire du script actuel
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Répertoire racine du projet (massive-gcp)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

# Répertoire 'out'
OUT_DIR = os.path.join(ROOT_DIR, "out")

# === 1. Charger le CSV ===
# conc.csv doit contenir : PARAM,AVG_TIME,RUN,FAILED
csv_path = os.path.join(OUT_DIR, "fanout.csv")
df = pd.read_csv(csv_path)

# Filtrer les runs réussis
df_ok = df[df["FAILED"] == 0].copy()

# Nettoyer AVG_TIME
df_ok["AVG_TIME_NUM"] = (
    df_ok["AVG_TIME"]
    .astype(str)
    .str.replace("ms", "", regex=False)
    .astype(float)/1000
)

# Moyenne + std
stats = (
    df_ok
    .groupby("PARAM")["AVG_TIME_NUM"]
    .agg(["mean", "std"])
    .reset_index()
    .sort_values("PARAM")
)

# Graphique
plt.figure(figsize=(10, 6))

x_labels = stats["PARAM"].astype(str)
x_pos = range(len(x_labels))

plt.bar(
    x_pos,
    stats["mean"],
    yerr=stats["std"],
    capsize=5
)
import numpy as np
y_min = 0
y_max = stats["mean"].max() + stats["std"].max()
plt.yticks(np.arange(y_min, y_max + 1, 1))
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.xticks(x_pos, x_labels)
plt.xlabel("Nombre de followees par utilisateur")
plt.ylabel("Temps moyen par requête (s)")
plt.title("Temps moyen par requête en fonction du nombre de followees")

plt.tight_layout()

png_path = os.path.join(OUT_DIR, "fanout.png")
plt.savefig(png_path, dpi=150)

print(f"Graph saved to: {png_path}")
