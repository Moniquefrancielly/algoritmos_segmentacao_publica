import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import adjusted_rand_score, silhouette_score

rfm = pd.read_csv("data/processed/rfm_clusters.csv")
df = pd.read_csv("data/processed/limpo.csv")
X = np.load("data/processed/X.npy")

# --- A) DBSCAN: sensibilidade ao min_samples (eps fixo em 0.5) ---
linhas = []
for ms in [4, 6, 8, 10, 12]:
    lab = DBSCAN(eps=0.5, min_samples=ms).fit_predict(X)
    m = lab != -1
    n = len(set(lab[m]))
    sil = silhouette_score(X[m], lab[m]) if n >= 2 else np.nan
    linhas.append({"min_samples": ms, "Nº grupos": n,
                   "Ruído (%)": round(100 * (~m).mean(), 2),
                   "Silhouette": round(sil, 3)})
a = pd.DataFrame(linhas); print(a)
a.to_csv("outputs/tables/robustez_min_samples.csv", index=False)

# --- B) K-Means (k=4): estabilidade ao trocar as variáveis ---
extra = df.groupby("CustomerID").agg(Produtos=("StockCode", "nunique")).reset_index()
b = rfm.merge(extra, on="CustomerID")
b["TicketMedio"] = b["Monetary"] / b["Frequency"]

conjuntos = {
    "RFM (base)": ["Recency", "Frequency", "Monetary"],
    "RF": ["Recency", "Frequency"],
    "RM": ["Recency", "Monetary"],
    "FM": ["Frequency", "Monetary"],
    "RFM + TicketMedio": ["Recency", "Frequency", "Monetary", "TicketMedio"],
    "RFM + Produtos": ["Recency", "Frequency", "Monetary", "Produtos"],
}
res = []
for nome, cols in conjuntos.items():
    Xc = StandardScaler().fit_transform(np.log1p(b[cols]))
    lab = KMeans(n_clusters=4, n_init=10, random_state=42).fit_predict(Xc)
    res.append({"Variáveis": nome,
                "ARI vs RFM base": round(adjusted_rand_score(rfm["KMeans"], lab), 3),
                "Silhouette": round(silhouette_score(Xc, lab), 3)})
r = pd.DataFrame(res); print(r)
r.to_csv("outputs/tables/robustez_variaveis.csv", index=False)