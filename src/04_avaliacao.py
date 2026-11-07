import numpy as np, pandas as pd
import matplotlib.pyplot as plt, seaborn as sns
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import (silhouette_score, davies_bouldin_score,
                             calinski_harabasz_score, adjusted_rand_score)

rfm = pd.read_csv("data/processed/rfm_clusters.csv")
X = np.load("data/processed/X.npy")

# ---------- 1. Métricas (DBSCAN: só sobre pontos não-ruído) ----------
def metricas(X, labels, nome):
    mask = labels != -1
    n_cl = len(set(labels[mask]))
    out = {"Algoritmo": nome, "Nº grupos": n_cl,
           "Ruído (%)": round(100 * (~mask).mean(), 2)}
    if n_cl >= 2:
        out["Silhouette"] = silhouette_score(X[mask], labels[mask])
        out["Davies-Bouldin"] = davies_bouldin_score(X[mask], labels[mask])
        out["Calinski-Harabasz"] = calinski_harabasz_score(X[mask], labels[mask])
    return out

tab = pd.DataFrame([metricas(X, rfm["KMeans"].values, "K-Means"),
                    metricas(X, rfm["DBSCAN"].values, "DBSCAN")]).round(3)
print(tab); tab.to_csv("outputs/tables/metricas.csv", index=False)

# ---------- 2. Estabilidade ----------
k = rfm["KMeans"].nunique()
base = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(X)
ari_seeds = [adjusted_rand_score(base, KMeans(n_clusters=k, n_init=10, random_state=s).fit_predict(X))
             for s in range(1, 11)]
print(f"K-Means ARI entre sementes: {np.mean(ari_seeds):.3f} ± {np.std(ari_seeds):.3f}")

# Sensibilidade a parâmetros: K-Means variando k, DBSCAN variando eps
est = []
for kk in range(2, 9):
    est.append({"Algoritmo": "K-Means", "Parâmetro": f"k={kk}",
                **metricas(X, KMeans(n_clusters=kk, n_init=10, random_state=42).fit_predict(X), "K-Means")})
for e in [0.2, 0.3, 0.4, 0.5, 0.6]:
    est.append({"Algoritmo": "DBSCAN", "Parâmetro": f"eps={e}",
                **metricas(X, DBSCAN(eps=e, min_samples=6).fit_predict(X), "DBSCAN")})
pd.DataFrame(est).round(3).to_csv("outputs/tables/sensibilidade.csv", index=False)

# Concordância entre algoritmos (somente não-ruído)
m = rfm["DBSCAN"] != -1
print("ARI K-Means x DBSCAN:", adjusted_rand_score(rfm.loc[m, "KMeans"], rfm.loc[m, "DBSCAN"]))

# ---------- 3. Perfis dos grupos ----------
for alg in ["KMeans", "DBSCAN"]:
    perfil = rfm.groupby(alg)[["Recency", "Frequency", "Monetary"]].agg(["mean", "median"]).round(1)
    perfil[("Clientes", "")] = rfm.groupby(alg).size()
    print(f"\nPerfil {alg}\n", perfil)
    perfil.to_csv(f"outputs/tables/perfil_{alg}.csv")

# ---------- 4. Gráficos ----------
pca = PCA(n_components=2, random_state=42)
Z = pca.fit_transform(X)
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
for a, alg in zip(ax, ["KMeans", "DBSCAN"]):
    sns.scatterplot(x=Z[:, 0], y=Z[:, 1], hue=rfm[alg], palette="tab10", s=8, ax=a, legend="full")
    a.set_title(f"{alg} (projeção PCA)")
plt.tight_layout(); plt.savefig("outputs/figures/clusters_pca.png", dpi=200)

fig, ax = plt.subplots(1, 3, figsize=(15, 4))
for a, v in zip(ax, ["Recency", "Frequency", "Monetary"]):
    sns.boxplot(data=rfm, x="KMeans", y=np.log1p(rfm[v]), ax=a); a.set_title(f"{v} (log) por grupo")
plt.tight_layout(); plt.savefig("outputs/figures/boxplot_rfm_kmeans.png", dpi=200)