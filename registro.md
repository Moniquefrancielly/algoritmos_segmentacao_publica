# Registro de execução: Implementação e análise computacional

Documento com os procedimentos e parâmetros efetivamente executados, para uso na metodologia do artigo.

## 1. Dataset

- Base: Online Retail II (UCI Machine Learning Repository)
- Arquivo: `online_retail_II.xlsx`, com duas abas (2009-2010 e 2010-2011), concatenadas
- Primeira transação: 2009-12-01 07:45
- Última transação: 2011-12-09 12:50
- Registros brutos: 1.067.371

## 2. Limpeza dos dados (`src/01_limpeza.py`)

| Etapa | Registros removidos |
|---|---|
| Sem identificação de cliente (CustomerID nulo) | 243.007 |
| Cancelamentos (fatura iniciada por "C") | 18.744 |
| Quantidade ou preço unitário menor ou igual a zero | 71 |

- Registros finais: **805.549**
- Clientes analisados: **5.878**
- Variável criada: `TotalPrice = Quantity × UnitPrice`

## 3. Engenharia de características: RFM (`src/02_rfm.py`)

- Data de referência: 2011-12-10 (um dia após a última transação)
- Recency: dias entre a data de referência e a última compra do cliente
- Frequency: número de faturas distintas do cliente
- Monetary: soma de `TotalPrice` do cliente

## 4. Pré-processamento (`src/03_clustering.py`)

- Transformação `log1p` aplicada a Recency, Frequency e Monetary (variáveis muito assimétricas)
- Padronização com `StandardScaler`
- Matriz final: 5.878 clientes × 3 variáveis

## 5. K-Means

- Parâmetros: `n_init=10`, `random_state=42`
- Valores de k testados: 2 a 10
- Critérios de escolha: método do cotovelo e Silhouette

| k | Silhouette |
|---|---|
| 2 | 0,4381 |
| 3 | 0,3478 |
| 4 | 0,3653 |
| 5 | 0,3421 |
| 6 | 0,3336 |
| 7 | 0,3052 |
| 8 | 0,2970 |
| 9 | 0,2913 |
| 10 | 0,2918 |

- k indicado pelo Silhouette: **2**
- k adotado na análise de perfis: **4**, escolhido pela interpretabilidade dos grupos (decisão do pesquisador, não do critério estatístico)

## 6. DBSCAN

- Parâmetros: `eps=0.5`, `min_samples=6`, distância euclidiana (padrão do scikit-learn)
- `eps` escolhido a partir do gráfico k-distance (`outputs/figures/dbscan_kdistance.png`) e dos percentis da distância ao 6º vizinho:

| Percentil | Distância |
|---|---|
| 80 | 0,196 |
| 90 | 0,262 |
| 95 | 0,344 |
| 97 | 0,422 |
| 99 | 0,663 |

- Resultado: 2 grupos (4.196 e 1.616 clientes) e 66 clientes classificados como ruído (1,12%)

## 7. Métricas de avaliação (`outputs/tables/metricas.csv`)

| Algoritmo | Nº grupos | Ruído (%) | Silhouette | Davies-Bouldin | Calinski-Harabasz |
|---|---|---|---|---|---|
| K-Means (k=4) | 4 | 0,0 | 0,365 | 0,930 | 5061,717 |
| DBSCAN | 2 | 1,12 | 0,279 | 1,008 | 2904,335 |

Observações:
- Para o DBSCAN, as métricas foram calculadas apenas sobre os pontos não classificados como ruído.
- Os algoritmos têm números de grupos diferentes (4 e 2). Para comparação mais equilibrada, ver K-Means com k=2 em `outputs/tables/sensibilidade.csv` (Silhouette 0,438).

## 8. Estabilidade e concordância

- Estabilidade do K-Means entre sementes: ARI médio de **0,995 ± 0,002** (10 sementes, de 1 a 10, comparadas à execução base com semente 42)
- Concordância K-Means × DBSCAN: ARI de **0,150** (apenas pontos não ruído)
- Sensibilidade a parâmetros: K-Means com k de 2 a 8 e DBSCAN com eps de 0,2 a 0,6 (`outputs/tables/sensibilidade.csv`)

## 9. Perfis encontrados (medianas)

### K-Means (k=4)

| Grupo | Clientes | Recência (dias) | Frequência | Monetary (£) | Interpretação |
|---|---|---|---|---|---|
| 0 | 1.188 | 16,5 | 13 | 5.126,8 | Alto valor / fiéis |
| 3 | 1.251 | 24 | 3 | 743,2 | Ativos recentes, valor moderado |
| 2 | 1.465 | 185 | 5 | 1.509,0 | Em risco (sem comprar há cerca de 6 meses) |
| 1 | 1.974 | 404 | 1 | 283,6 | Inativos / compra única |

### DBSCAN

| Grupo | Clientes | Recência (dias) | Frequência | Monetary (£) | Interpretação |
|---|---|---|---|---|---|
| -1 (ruído) | 66 | 23 | 35 | 35.008,2 | Outliers de altíssimo valor |
| 0 | 4.196 | 60 | 5 | 1.376,3 | Base principal, sem diferenciação interna |
| 1 | 1.616 | 388 | 1 | 231,8 | Compra única / inativos |

## 10. Ambiente

- Python 3.14
- Bibliotecas e versões: ver `requirements.txt`
- Semente aleatória: 42
- Ordem de execução: `01_limpeza.py` → `02_rfm.py` → `03_clustering.py` → `04_avaliacao.py`

## 11. Achados principais

- O Silhouette indica k=2 para o K-Means, mas k=4 gera perfis mais interpretáveis.
- O K-Means é estável entre sementes (ARI próximo de 1).
- O DBSCAN separa os clientes de compra única e isola os clientes de altíssimo valor como ruído, mas não divide a base ativa.
- A concordância entre os dois algoritmos é baixa (ARI 0,150), pois eles capturam estruturas diferentes.