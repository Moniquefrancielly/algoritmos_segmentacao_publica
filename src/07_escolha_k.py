import numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (silhouette_score, davies_bouldin_score,
                             calinski_harabasz_score, adjusted_rand_score)

X = np.load("data/processed/X.npy")
rng = np.random.default_rng(42)
linhas = []
for k in range(2, 9):
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
    base = km.labels_
    aris = []
    for b in range(20):  # reamostragem: 80% dos clientes, 20 vezes
        idx = rng.choice(len(X), size=int(0.8 * len(X)), replace=False)
        lab = KMeans(n_clusters=k, n_init=10, random_state=b).fit_predict(X[idx])
        aris.append(adjusted_rand_score(base[idx], lab))
    linhas.append({"k": k,
                   "Inércia": round(km.inertia_, 1),
                   "Silhouette": round(silhouette_score(X, base), 3),
                   "Davies-Bouldin": round(davies_bouldin_score(X, base), 3),
                   "Calinski-Harabasz": round(calinski_harabasz_score(X, base), 1),
                   "ARI reamostragem (média)": round(np.mean(aris), 3),
                   "ARI reamostragem (dp)": round(np.std(aris), 3)})
t = pd.DataFrame(linhas)
print(t.to_string(index=False))
t.to_csv("outputs/tables/escolha_k_completa.csv", index=False)