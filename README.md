# Segmentação de consumidores com aprendizado não supervisionado
 
Identificação de perfis de consumidores no comércio eletrônico a partir de dados transacionais (Online Retail II), comparando os algoritmos **K-Means** e **DBSCAN** sobre variáveis **RFM** (Recência, Frequência e Valor Monetário).
 
Este repositório contém a parte de **implementação e análise computacional** do artigo: limpeza dos dados, construção do RFM, normalização, agrupamento, métricas de avaliação, estabilidade e perfis dos grupos.
 
---
 
## Pergunta de pesquisa
 
Como diferentes algoritmos de aprendizado não supervisionado identificam e diferenciam perfis de comportamento de consumo a partir de dados transacionais do comércio eletrônico?
 
## Dataset
 
- **Online Retail II**, do UCI Machine Learning Repository
- Link: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- Transações de uma empresa britânica de e-commerce, de 01/12/2009 a 09/12/2011
- Aproximadamente 1,07 milhão de registros, cada um representando um produto em uma fatura
> O dataset **não está no repositório** (é pesado). Baixe-o e salve como `data/raw/online_retail_II.xlsx`.
 
---
 
## Estrutura do repositório
 
```
.
├── artigo/                       # versão final do artigo (IEEE) em PDF 
├── data/
│   ├── raw/                      # online_retail_II.xlsx (baixar da UCI, não versionado)
│   └── processed/                # dados intermediários e resultados dos grupos
│       ├── limpo.csv             # dados limpos (não versionado)
│       ├── rfm.csv               # tabela RFM por cliente
│       ├── X.npy                 # matriz normalizada (não versionada)
│       └── rfm_clusters.csv      # RFM + rótulos de K-Means e DBSCAN
├── outputs/
│   ├── figures/                  # gráficos (PNG)
│   └── tables/                   # tabelas de métricas e perfis (CSV)
├── src/
│   ├── 01_limpeza.py
│   ├── 02_rfm.py
│   ├── 03_clustering.py
│   └── 04_avaliacao.py
├── registro.md                   # registro de procedimentos e parâmetros executados
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```
 
---
 
## O que faz cada script
 
| Script | Função resumida | Entrada | Saída |
|---|---|---|---|
| `01_limpeza.py` | Lê as duas abas do Excel, remove registros sem cliente, cancelamentos e quantidades/preços inválidos, cria `TotalPrice` | `data/raw/online_retail_II.xlsx` | `data/processed/limpo.csv` |
| `02_rfm.py` | Calcula Recência, Frequência e Valor Monetário por cliente | `limpo.csv` | `data/processed/rfm.csv` |
| `03_clustering.py` | Aplica `log1p` + `StandardScaler`, escolhe k (cotovelo e Silhouette), executa K-Means e DBSCAN | `rfm.csv` | `X.npy`, `rfm_clusters.csv`, `kmeans_escolha_k.csv`, 2 figuras |
| `04_avaliacao.py` | Calcula métricas, estabilidade, concordância entre algoritmos, perfis dos grupos e gráficos | `rfm_clusters.csv`, `X.npy` | tabelas e figuras finais |
 
### Definição das variáveis RFM
 
- **Recency:** dias entre a data de referência (10/12/2011, um dia após a última transação) e a última compra do cliente
- **Frequency:** número de faturas distintas do cliente
- **Monetary:** soma de `Quantity × UnitPrice` do cliente
---
 
## Como rodar
 
### 1. Pré-requisitos
 
- Python 3.10 ou superior (desenvolvido com Python 3.14)
- Git
### 2. Clonar e preparar o ambiente
 
```bash
git clone https://github.com/Moniquefrancielly/algoritmos_segmentacao_publica.git
cd algoritmos_segmentacao_publica
 
python -m venv .venv
```
 
Ativar o ambiente virtual:
 
```bash
# Windows (PowerShell)
.venv\Scripts\activate
 
# Linux / macOS
source .venv/bin/activate
```
 
Instalar as dependências:
 
```bash
pip install -r requirements.txt
```
 
### 3. Baixar o dataset
 
1. Acesse https://archive.ics.uci.edu/dataset/502/online+retail+ii e clique em **Download**
2. Extraia o `.zip`
3. Coloque `online_retail_II.xlsx` em `data/raw/`
### 4. Criar as pastas de saída
 
Os scripts não criam pastas sozinhos. Se elas não existirem, crie antes de rodar.
 
```powershell
# Windows (PowerShell)
mkdir data\raw, data\processed, outputs\figures, outputs\tables
```
 
```bash
# Linux / macOS
mkdir -p data/raw data/processed outputs/figures outputs/tables
```
 
### 5. Executar os scripts, em ordem
 
Rode **um de cada vez**, esperando terminar. Cada um depende do arquivo gerado pelo anterior.
 
```bash
python src/01_limpeza.py
python src/02_rfm.py
python src/03_clustering.py
python src/04_avaliacao.py
```
 
---
 
## O que esperar ao rodar
 
### `01_limpeza.py` (leva de 30 s a alguns minutos, a leitura do Excel é lenta)
 
```
Registros brutos: 1067371
Sem cliente removidos: 243007
Cancelamentos removidos: 18744
Qtd/preço inválidos: 71
Registros finais: 805549 | Clientes: 5878
```
 
### `02_rfm.py`
 
Imprime estatísticas descritivas (`count`, `mean`, `min`, `max`...) de Recency, Frequency e Monetary, com 5.878 clientes.
 
### `03_clustering.py`
 
```
k pelo Silhouette: 2
 k  Silhouette
 2      0.4381
 3      0.3478
 4      0.3653
 5      0.3421
 6      0.3336
 7      0.3052
 8      0.2970
 9      0.2913
10      0.2918
k usado nos perfis: 4
percentil 80: 0.196
percentil 90: 0.262
percentil 95: 0.344
percentil 97: 0.422
percentil 99: 0.663
DBSCAN
 0    4196
 1    1616
-1      66
```
 
(`-1` indica ruído no DBSCAN.)
 
### `04_avaliacao.py`
 
Imprime a tabela de métricas, o ARI de estabilidade do K-Means (≈ 0,995 ± 0,002), o ARI entre K-Means e DBSCAN (≈ 0,150) e os perfis dos grupos. Pode aparecer um `Pandas4Warning` sobre MultiIndex; é apenas um alerta de versão e não afeta os resultados.
 
> Os resultados devem ser idênticos aos acima em qualquer máquina, pois a semente aleatória é fixa (`random_state=42`).
 
---
 
## Arquivos gerados
 
### Tabelas (`outputs/tables/`)
 
| Arquivo | Conteúdo |
|---|---|
| `kmeans_escolha_k.csv` | Inércia e Silhouette do K-Means para k de 2 a 10 |
| `metricas.csv` | Nº de grupos, % de ruído, Silhouette, Davies-Bouldin e Calinski-Harabasz de cada algoritmo |
| `sensibilidade.csv` | Métricas do K-Means variando k (2 a 8) e do DBSCAN variando eps (0,2 a 0,6) |
| `perfil_KMeans.csv` | Média e mediana de R, F e M, e tamanho de cada grupo do K-Means |
| `perfil_DBSCAN.csv` | Idem, para o DBSCAN (inclui o grupo de ruído `-1`) |
 
### Figuras (`outputs/figures/`)
 
| Arquivo | Conteúdo |
|---|---|
| `kmeans_escolha_k.png` | Método do cotovelo e Silhouette por k |
| `dbscan_kdistance.png` | Gráfico k-distance, usado para escolher o `eps` |
| `clusters_pca.png` | Grupos de K-Means e DBSCAN projetados em 2 dimensões (PCA) |
| `boxplot_rfm_kmeans.png` | Distribuição de R, F e M (em log) por grupo do K-Means |
 
---
 
## Parâmetros utilizados
 
| Item | Valor |
|---|---|
| Transformação | `log1p` seguida de `StandardScaler` |
| Semente aleatória | 42 |
| K-Means | `n_init=10`; k testado de 2 a 10; **k adotado = 4** |
| DBSCAN | `eps=0.5`, `min_samples=6`, distância euclidiana |
| Estabilidade | ARI entre execuções do K-Means com sementes de 1 a 10 |
 
**Sobre a escolha de k:** o Silhouette indica k = 2 (0,438), mas adotou-se k = 4 pela interpretabilidade dos perfis (Silhouette 0,365). Essa é uma decisão do pesquisador, documentada no `registro.md`. Para trocar o k, edite a linha `k_final = 4` em `src/03_clustering.py` e rode novamente os scripts 03 e 04.
 
**Sobre o eps:** o valor 0,5 foi escolhido a partir do gráfico k-distance e dos percentis da distância ao 6º vizinho. Ele corresponde a cerca de 1,1% de ruído.
 
---
 
## Resumo dos resultados
 
### Métricas
 
| Algoritmo | Nº grupos | Ruído (%) | Silhouette | Davies-Bouldin | Calinski-Harabasz |
|---|---|---|---|---|---|
| K-Means (k=4) | 4 | 0,0 | 0,365 | 0,930 | 5061,717 |
| DBSCAN | 2 | 1,12 | 0,279 | 1,008 | 2904,335 |
 
Para o DBSCAN, as métricas consideram apenas os pontos que não são ruído. Para uma comparação com o mesmo número de grupos, consulte K-Means com k = 2 em `sensibilidade.csv`.
 
### Perfis do K-Means (medianas)
 
| Grupo | Clientes | Recência (dias) | Frequência | Monetary (£) | Interpretação |
|---|---|---|---|---|---|
| 0 | 1.188 | 16,5 | 13 | 5.126,8 | Alto valor / fiéis |
| 3 | 1.251 | 24 | 3 | 743,2 | Ativos recentes, valor moderado |
| 2 | 1.465 | 185 | 5 | 1.509,0 | Em risco |
| 1 | 1.974 | 404 | 1 | 283,6 | Inativos / compra única |
 
### Perfis do DBSCAN (medianas)
 
| Grupo | Clientes | Recência (dias) | Frequência | Monetary (£) | Interpretação |
|---|---|---|---|---|---|
| -1 (ruído) | 66 | 23 | 35 | 35.008,2 | Outliers de altíssimo valor |
| 0 | 4.196 | 60 | 5 | 1.376,3 | Base principal, sem diferenciação interna |
| 1 | 1.616 | 388 | 1 | 231,8 | Compra única / inativos |
 
### Estabilidade e concordância
 
- K-Means entre sementes: ARI = 0,995 ± 0,002 (estável)
- K-Means × DBSCAN: ARI = 0,150 (baixa concordância; os algoritmos capturam estruturas diferentes)
Os rótulos de interpretação (por exemplo, "Em risco") são leituras dos autores com base nas medianas, não saídas dos algoritmos.
 
---
 
## Solução de problemas
 
| Erro | Causa | Solução |
|---|---|---|
| `FileNotFoundError` em `online_retail_II.xlsx` | Dataset não está em `data/raw/` | Baixar e salvar com o nome exato |
| `OSError: Cannot save file into a non-existent directory` | Pastas de saída não existem | Executar os comandos `mkdir` do passo 4 |
| `ModuleNotFoundError` | Ambiente virtual inativo ou dependências não instaladas | Ativar o `.venv` e rodar `pip install -r requirements.txt` |
| Script 02, 03 ou 04 falha por falta de arquivo | Scripts rodados fora de ordem | Rodar na ordem 01, 02, 03, 04 |
 
Execute sempre os comandos a partir da **raiz do repositório**, pois os caminhos nos scripts são relativos a ela.
 
---
 
## Reprodutibilidade
 
Para validar do zero: apague `data/processed/` e `outputs/`, recrie as pastas e rode os quatro scripts em ordem. Os números devem coincidir com os deste README e do `registro.md`.
 
## Tecnologias
 
Python, Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn e OpenPyXL.
 
## Documentação complementar
 
O arquivo [`registro.md`](registro.md) detalha todos os procedimentos e parâmetros efetivamente executados, e serve de base para a seção de metodologia do artigo.
 
Claude terminou a resposta
