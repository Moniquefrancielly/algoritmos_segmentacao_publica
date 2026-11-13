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
- k adotado na análise de perfis: **4**, escolhido pela interpretabilidade dos grupos (decisão dos pesquisadores, não do critério estatístico)
- Justificativa do k = 4: o Silhouette foi máximo em k = 2 (0,438), que separa apenas
  clientes ativos de inativos. Entre k ≥ 3, o maior valor ocorre em k = 4 (0,365, contra
  0,348 em k = 3 e 0,342 em k = 5). Adotou-se k = 4 por ser esse máximo local e por gerar
  perfis mais interpretáveis, ao custo de uma queda de 0,073 no Silhouette em relação a k = 2.
  A decisão é dos autores, não do critério estatístico.
  - Perfil de k = 2 (medianas): grupo 0, 2.352 clientes (40,0%), recência 24 dias, frequência 8, Monetary £ 2.871,5; grupo 1, 3.526 clientes (60,0%), recência 295,5 dias, frequência 2, Monetary £ 418,1. Separa clientes mais engajados dos menos engajados.
- Tabela cruzada com k = 4: os grupos 0 e 1 estão contidos integralmente em cada grupo de k = 2; os grupos 2 e 3 se dividem entre os dois (592/873 e 572/679).

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
- Justificativa do `min_samples = 6`: regra prática de 2 × número de dimensões
  (2 × 3 variáveis), citada na literatura de DBSCAN (Sander et al., 1998).
- Sensibilidade ao `min_samples` (eps fixo em 0,5; `outputs/tables/robustez_min_samples.csv`):

| min_samples | Nº grupos | Ruído (%) | Silhouette |
|---|---|---|---|
| 4 | 2 | 1,00 | 0,278 |
| 6 | 2 | 1,12 | 0,279 |
| 8 | 2 | 1,29 | 0,278 |
| 10 | 2 | 1,48 | 0,278 |
| 12 | 2 | 1,55 | 0,278 |

  O resultado manteve-se em 2 grupos em toda a faixa testada, indicando pouca sensibilidade
  a esse parâmetro (com eps fixo).

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
- - Sensibilidade a parâmetros: K-Means com k de 2 a 8 e DBSCAN com eps de 0,2 a 0,6 (`outputs/tables/sensibilidade.csv`). Essa análise descreve como as métricas variam, mas não mede a estabilidade das partições.
- Estabilidade do K-Means (k = 4) a mudanças nas variáveis (`src/05_robustez.py`,
  `outputs/tables/robustez_variaveis.csv`). Mesma transformação (log1p + StandardScaler),
  ARI em relação à partição do RFM base: 

| Variáveis | ARI vs RFM base |
|---|---|
| RFM (base) | 1,000 |
| RF | 0,604 |
| RM | 0,706 |
| FM | 0,356 |
| RFM + ticket médio | 0,430 |
| RFM + produtos | 0,686 |

- O ARI = 1,000 na linha base confirma que o script reproduz a partição original.
- Leitura: a omissão da Recência (FM) foi a que mais alterou os grupos. O ticket médio é
  função de variáveis já presentes (em log, log M − log F), então o ARI menor reflete mudança
  de pesos, não informação nova.
- O Silhouette dessa tabela não é comparável entre as linhas, pois cada uma usa um espaço
  de variáveis diferente.

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

- Scripts 01 a 04: Python 3.14 (ver `requirements.txt` para as bibliotecas)
- Script 05 (`05_robustez.py`), executado em outra máquina: Python 3.14.7, pandas 3.1.1,
  numpy 2.5.4, scikit-learn 1.9.1, scipy 1.18.1, matplotlib 3.11.2, seaborn 0.13.2
  e openpyxl 3.1.5
- Semente aleatória: 42
- Ordem de execução: `01_limpeza.py` → `02_rfm.py` → `03_clustering.py` →
  `04_avaliacao.py` → `05_robustez.py`

## 11. Achados principais

- O Silhouette indica k=2 para o K-Means, mas k=4 gera perfis mais interpretáveis.
- O K-Means é estável entre sementes (ARI próximo de 1).
- O DBSCAN separa os clientes de compra única e isola os clientes de altíssimo valor como ruído, mas não divide a base ativa.
- A concordância entre os dois algoritmos é baixa (ARI 0,150), pois eles capturam estruturas diferentes.
- O DBSCAN é pouco sensível ao `min_samples` (4 a 12, com eps = 0,5), mas muito sensível ao `eps`.
- Os perfis do K-Means são moderadamente estáveis a mudanças nas variáveis (ARI de 0,36 a 0,71);
  a omissão da Recência foi a que mais os alterou.