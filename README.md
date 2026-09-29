# Análise de Transações – Fintech

Pipeline em Pandas/NumPy/Matplotlib: limpeza, alinhamento temporal, filtros bitwise,
pivot por risco, Z-Score por estado e gráfico com média móvel de 7 dias.

## Como executar
```bash
pip install -r requirements.txt
python gerar_dados.py   # script fornecido pela Engenharia
python pipeline.py      # executa o pipeline
```
Saídas: `grafico_transacoes.png`, `pivot_risco.csv`, `anomalias.csv`.

## Decisões
- Leitura com `encoding="latin1"` e `dtype` categórico/string para reduzir memória.
- Mediana de `valor` imputada por estado via `groupby().transform("median")`.
- `datetime64[ns]` forçado com `astype` (pandas 3 infere outras resoluções) + `tz_localize("America/Sao_Paulo")`.
- Filtro com `&` e `|` (vetorizado); Z-Score com `transform` (sem laços), σ populacional (`ddof=0`).
- `risco_dict` cobre C100–C104 (clientes do script de geração); clientes fora do dicionário viram "Não classificado".
- `cotacoes.csv` é gerado pelo script, mas os requisitos não o utilizam.
