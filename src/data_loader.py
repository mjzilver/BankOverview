import pandas as pd
import os
from glob import glob

from utils import format_zakelijk

CSV_GLOB = "*.csv"
DATE_COL = "Datum"
AMOUNT_COL = "Bedrag"
COUNTERPARTY_COL = "Naam tegenpartij"
IBAN_COL = "IBAN/BBAN"
COUNTERPARTY_IBAN_COL = "Tegenrekening IBAN/BBAN"


def load_csvs(directory):
    all_files = glob(os.path.join(directory, CSV_GLOB))
    dfs = []
    for file in all_files:
        df = pd.read_csv(file, sep=",", dtype=str, encoding="latin1")
        df.columns = df.columns.str.strip()
        if {"Datum", "Bedrag", "Naam tegenpartij"}.issubset(df.columns):
            dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def clean_transactions(df):
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    df[AMOUNT_COL] = df[AMOUNT_COL].str.replace(",", ".").astype(float, errors="ignore")
    df[COUNTERPARTY_COL] = df[COUNTERPARTY_COL].fillna("Onbekend")
    df = df.dropna(subset=[DATE_COL, AMOUNT_COL])

    if IBAN_COL in df.columns and COUNTERPARTY_IBAN_COL in df.columns:
        own_ibans = df[IBAN_COL].dropna().unique()
        df = df[~df[COUNTERPARTY_IBAN_COL].isin(own_ibans)]

    df["Maand"] = df[DATE_COL].dt.to_period("M")
    return df


def merge_and_clean_labels(summary_df, label_df):
    df = summary_df.merge(label_df, on="Tegenpartij", how="left")
    df["Label"] = df["Label"].fillna("").str.strip().replace("", "geen label")
    df["Zakelijk_NL"] = df["Zakelijk"].apply(format_zakelijk)
    return df
