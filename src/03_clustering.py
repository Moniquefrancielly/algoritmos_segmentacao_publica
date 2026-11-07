import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors

SEED = 42
rfm = pd.read_csv("data/processed/rfm.csv")
X = StandardScaler().fit_transform(np.log1p(rfm[["Recency", "Frequency", "Monetary"]]))
np.save("data/processed/X.npy", X)

# ---------- K-MEANS: escolha de k (cotovelo + silhouette) ----------
ks = range(2, 11)
inercia, sil = [], []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(X)
    inercia.append(km.inertia_)
    sil.append(silhouette_score(X, km.labels_))

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(ks, inercia, "o-"); ax[0].set_title("Método do cotovelo"); ax[0].set_xlabel("k")
ax[1].plot(ks, sil, "o-");     ax[1].set_title("Silhouette por k");   ax[1].set_xlabel("k")
plt.tight_layout(); plt.savefig("outputs/figures/kmeans_escolha_k.png", dpi=200)

k_auto = list(ks)[int(np.argmax(sil))]
print("k pelo Silhouette:", k_auto)

# Salva a tabela de silhouette/inércia por k (útil para o registro e para a sua dupla)
pd.DataFrame({"k": list(ks), "Inercia": inercia, "Silhouette": sil}).round(4).to_csv(
    "outputs/tables/kmeans_escolha_k.csv", index=False)
print(pd.DataFrame({"k": list(ks), "Silhouette": np.round(sil, 4)}).to_string(index=False))

k_final = 4   # escolhido para interpretação; k_auto fica registrado na discussão
print("k usado nos perfis:", k_final)
rfm["KMeans"] = KMeans(n_clusters=k_final, n_init=10, random_state=SEED).fit_predict(X)

# ---------- DBSCAN: escolha de eps (gráfico k-distance) ----------
min_samples = 6   # regra comum: 2 * nº de dimensões
dist, _ = NearestNeighbors(n_neighbors=min_samples).fit(X).kneighbors(X)
plt.figure(figsize=(6, 4))
plt.plot(np.sort(dist[:, -1])); plt.title("k-distance (DBSCAN)"); plt.ylabel("distância")
plt.savefig("outputs/figures/dbscan_kdistance.png", dpi=200)

d = np.sort(dist[:, -1])
for p in [80, 90, 95, 97, 99]:
    print(f"percentil {p}: {np.percentile(d, p):.3f}")

eps = 0.5   # AJUSTE olhando o "joelho" do gráfico acima
rfm["DBSCAN"] = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X)
print(rfm["DBSCAN"].value_counts())   # -1 = ruído

rfm.to_csv("data/processed/rfm_clusters.csv", index=False)