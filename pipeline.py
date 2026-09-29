"""Pipeline de limpeza, transformação, agregação, anomalias e gráfico."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIAS = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta",
        4: "Sexta", 5: "Sábado", 6: "Domingo"}
risco_dict = {'C100': 'Baixo', 'C101': 'Alto', 'C102': 'Médio',
              'C103': 'Baixo', 'C104': 'Alto'}


def carregar(caminho="transacoes.csv"):
    df = pd.read_csv(
        caminho, encoding="latin1",
        dtype={"id_cliente": "string", "origem": "category",
               "estado_cliente": "category"},   # performance de memória
    )
    df["valor"] = df["valor"].fillna(
        df.groupby("estado_cliente", observed=True)["valor"].transform("median"))
    df["plataforma"] = "Mobile"
    return df


def transformar(df):
    df = df.copy()
    dt = pd.to_datetime(df["data_transacao"]).astype("datetime64[ns]")
    df["data_transacao"] = dt.dt.tz_localize("America/Sao_Paulo")
    df["dia_semana"] = df["data_transacao"].dt.dayofweek.map(DIAS)
    df["mes"] = df["data_transacao"].dt.month
    return df.drop_duplicates(keep="first").reset_index(drop=True)


def filtrar_setembro(df):
    mask = ((df["mes"] == 9)
            & ((df["estado_cliente"] == "SP") | (df["estado_cliente"] == "RJ"))
            & (df["valor"] > 5000))
    return df[mask]


def tabela_risco(df):
    df = df.copy()
    df["nivel_risco"] = df["id_cliente"].map(risco_dict).fillna("Não classificado")
    piv = pd.pivot_table(df, values="valor", index="mes", columns="nivel_risco",
                         aggfunc="sum", margins=True, margins_name="Total")
    return df, piv


def zscore_por_estado(df, col="valor", grupo="estado_cliente"):
    g = df.groupby(grupo, observed=True)[col]
    return (df[col] - g.transform("mean")) / g.transform(lambda s: s.std(ddof=0))


def grafico(df, saida="grafico_transacoes.png"):
    diario = df.set_index("data_transacao")["valor"].resample("D").sum()
    media = diario.rolling(7).mean()
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(diario.index, diario.values, color="tab:blue", alpha=.6,
            label="Total diário")
    ax.plot(media.index, media.values, color="tab:red", lw=2.2,
            label="Média móvel 7 dias")
    ax.set_ylim(bottom=0)
    ax.set_title("Valor total de transações por dia (R$)")
    ax.set_xlabel("Data"); ax.set_ylabel("Valor (R$)")
    ax.grid(alpha=.3); ax.legend()
    fig.autofmt_xdate(); fig.tight_layout()
    fig.savefig(saida, dpi=150)
    return fig


def main():
    df = transformar(carregar())
    print(f"Registros após limpeza: {len(df)} | tz: {df['data_transacao'].dt.tz}")
    print(df.head(), "\n")

    filtrado = filtrar_setembro(df)
    print(f"Setembro, SP/RJ, valor > 5000: {len(filtrado)} transações\n")

    df, piv = tabela_risco(df)
    print(piv.round(2), "\n")
    piv.to_csv("pivot_risco.csv")

    df["zscore"] = zscore_por_estado(df)
    anomalias = df[df["zscore"] > 2.5]
    print(f"Anomalias (Z > 2.5): {len(anomalias)}")
    anomalias.to_csv("anomalias.csv", index=False, encoding="utf-8-sig")

    grafico(df)
    print("Gráfico salvo em grafico_transacoes.png")


if __name__ == "__main__":
    main()
