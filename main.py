from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from glob import glob
import os

CSV_DIR = "data"
CSV_GLOB = "*.csv"
DATE_COL = "Datum"
AMOUNT_COL = "Bedrag"
COUNTERPARTY_COL = "Naam tegenpartij"
IBAN_COL = "IBAN/BBAN"
COUNTERPARTY_IBAN_COL = "Tegenrekening IBAN/BBAN"

st.set_page_config(page_title="Financieel Overzicht", layout="wide")


def load_all_csvs(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    all_files = glob(os.path.join(directory, CSV_GLOB))
    df_list = []
    for file in all_files:
        df = pd.read_csv(file, sep=",", dtype=str, encoding="latin1")
        df.columns = df.columns.str.strip()
        required_columns = {"Datum", "Bedrag", "Naam tegenpartij"}
        missing = required_columns - set(df.columns)
        if missing:
            st.warning(f"Skipping {file}, missing columns: {sorted(missing)}")
            continue
        df_list.append(df)
    return pd.concat(df_list, ignore_index=True)


def clean_and_prepare(df):
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], format="%Y-%m-%d", errors="coerce")
    df[AMOUNT_COL] = df[AMOUNT_COL].str.replace(",", ".").astype(float, errors="ignore")
    df[AMOUNT_COL] = pd.to_numeric(df[AMOUNT_COL], errors="coerce")
    df[COUNTERPARTY_COL] = df[COUNTERPARTY_COL].fillna("Onbekend")
    df = df.dropna(subset=[DATE_COL, AMOUNT_COL])

    if IBAN_COL in df.columns and COUNTERPARTY_IBAN_COL in df.columns:
        own_ibans = df[IBAN_COL].dropna().unique()
        df = df[~df[COUNTERPARTY_IBAN_COL].isin(own_ibans)]

    df["Maand"] = df[DATE_COL].dt.to_period("M")
    return df


def summarize_by_counterparty_per_month(df):
    monthly_by_party = (
        df.groupby(["Maand", COUNTERPARTY_COL])[AMOUNT_COL].sum().reset_index()
    )
    monthly_by_party.columns = ["Maand", "Tegenpartij", "Netto"]
    monthly_by_party["Maand"] = monthly_by_party["Maand"].astype(str)
    return monthly_by_party


def format_month(period_str):
    year, month = period_str.split("-")
    dutch_months = [
        "Alle maanden",
        "januari",
        "februari",
        "maart",
        "april",
        "mei",
        "juni",
        "juli",
        "augustus",
        "september",
        "oktober",
        "november",
        "december",
    ]
    return f"{dutch_months[int(month)]} {year}"


def main():
    st.title("Financieel Overzicht")

    df = load_all_csvs(CSV_DIR)
    df = clean_and_prepare(df)

    summary_df = summarize_by_counterparty_per_month(df)
    summary_df["Maand_NL"] = summary_df["Maand"].apply(format_month)
    summary_df = summary_df.sort_values(by=["Maand", "Netto"], ascending=[True, False])

    months_order = summary_df.drop_duplicates("Maand")[
        ["Maand", "Maand_NL"]
    ].sort_values("Maand")
    months_nl = months_order["Maand_NL"].tolist()
    selected_month_nl = st.selectbox("Filter op maand", ["Alle maanden"] + months_nl)

    filtered_df = summary_df.copy()
    if selected_month_nl != "Alle maanden":
        selected_month = summary_df[summary_df["Maand_NL"] == selected_month_nl][
            "Maand"
        ].iloc[0]
        filtered_df = filtered_df[filtered_df["Maand"] == selected_month]

    filtered_df = filtered_df.sort_values("Netto", ascending=False)

    st.subheader(f"Overzicht: Netto per tegenpartij voor {selected_month_nl}")
    if selected_month_nl == "Alle maanden":
        filtered_df = filtered_df.sort_values(
            ["Maand", "Netto"], ascending=[True, False]
        )
    else:
        filtered_df.drop(columns=["Maand_NL"], inplace=True)
    filtered_df = filtered_df.drop(columns=["Maand"])
    st.dataframe(filtered_df.style.format({"Netto": "{:,.2f}"}))

    if selected_month_nl != "Alle maanden":
        st.subheader(f"Grafiek: Netto per tegenpartij voor {selected_month_nl}")
        n_rows = len(filtered_df)
        fig_height = max(4, n_rows * 0.1)
        fig, ax = plt.subplots(figsize=(8, fig_height))
        colors = filtered_df["Netto"].apply(lambda x: "green" if x >= 0 else "red")
        bars = ax.barh(
            filtered_df["Tegenpartij"][::-1],
            filtered_df["Netto"][::-1],
            color=colors[::-1],
        )

        offset = 2

        for i, bar in enumerate(bars):
            width = bar.get_width()
            y = bar.get_y() + bar.get_height() / 2

            ax.annotate(
                f"{width:,.2f}€",
                xy=(width, y),
                xytext=(offset if width >= 0 else -offset, 0),
                textcoords="offset points",
                ha="left" if width >= 0 else "right",
                va="center",
                fontsize=4,
                color="black",
            )

            tegenpartij = filtered_df["Tegenpartij"].iloc[::-1].iloc[i]
            ax.annotate(
                tegenpartij[:50],
                xy=(0, y),
                xytext=(-offset if width >= 0 else offset, 0),
                textcoords="offset points",
                ha="right" if width >= 0 else "left",
                va="center",
                fontsize=4,
                color="black",
            )
        ax.set_yticks([])
        plt.yticks(fontsize=4)
        plt.tight_layout()
        st.pyplot(fig)

    st.subheader("Grafiek: Inkomsten, Uitgaven en Netto per maand")
    monthly = (
        summary_df.groupby(["Maand", "Maand_NL"])["Netto"]
        .agg(
            inkomsten=lambda x: x[x > 0].sum(),
            uitgaven=lambda x: x[x < 0].sum(),
            netto="sum",
        )
        .reset_index()
    )
    monthly = monthly.sort_values("Maand")

    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(monthly))  # posities op de x-as
    width = 0.25

    ax.bar(
        x - width, monthly["inkomsten"], width=width, label="Inkomsten", color="green"
    )
    ax.bar(x, monthly["uitgaven"].abs(), width=width, label="Uitgaven", color="red")
    netto_bars = ax.bar(
        x + width, monthly["netto"], width=width, label="Netto", color="blue"
    )

    for bar in netto_bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:,.0f}€",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3 if height > 0 else -10),  # offset
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            color="black",
        )

    ax.set_ylabel("Bedrag (€)")
    ax.set_xticks(x)
    ax.set_xticklabels(monthly["Maand_NL"], rotation=45, ha="right")
    ax.legend()
    st.pyplot(fig)


if __name__ == "__main__":
    main()
