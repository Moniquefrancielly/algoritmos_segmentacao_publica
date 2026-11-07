import pandas as pd

# O arquivo tem duas abas (2009-2010 e 2010-2011)
abas = pd.read_excel("data/raw/online_retail_II.xlsx", sheet_name=None)
df = pd.concat(abas.values(), ignore_index=True)
print("Registros brutos:", len(df))

df = df.rename(columns={"Invoice": "InvoiceNo", "Customer ID": "CustomerID",
                        "Price": "UnitPrice"})

# Remoções (registrar cada passo: vai para a metodologia)
n0 = len(df)
df = df.dropna(subset=["CustomerID"]);               print("Sem cliente removidos:", n0 - len(df)); n0 = len(df)
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]; print("Cancelamentos removidos:", n0 - len(df)); n0 = len(df)
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)];     print("Qtd/preço inválidos:", n0 - len(df))

df["CustomerID"] = df["CustomerID"].astype(int)
df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

print("Registros finais:", len(df), "| Clientes:", df["CustomerID"].nunique())
df.to_csv("data/processed/limpo.csv", index=False)