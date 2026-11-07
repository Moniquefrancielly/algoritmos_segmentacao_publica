import pandas as pd

df = pd.read_csv("data/processed/limpo.csv", parse_dates=["InvoiceDate"])

# Data de referência = 1 dia após a última transação
ref = df["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = df.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x: (ref - x.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("TotalPrice", "sum"),
).reset_index()

print(rfm.describe())
rfm.to_csv("data/processed/rfm.csv", index=False)