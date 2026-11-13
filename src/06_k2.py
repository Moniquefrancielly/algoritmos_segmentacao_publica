import numpy as np, pandas as pd
from sklearn.cluster import KMeans

rfm = pd.read_csv("data/processed/rfm_clusters.csv")
X = np.load("data/processed/X.npy")
rfm["K2"] = KMeans(n_clusters=2, n_init=10, random_state=42).fit_predict(X)

perfil = rfm.groupby("K2")[["Recency", "Frequency", "Monetary"]].median().round(1)
perfil["Clientes"] = rfm.groupby("K2").size()
print(perfil)
print(pd.crosstab(rfm["KMeans"], rfm["K2"]))