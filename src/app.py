import streamlit as st
import sqlite3
from data_loader import load_csvs, clean_transactions
from analysis import (
    filter_zakelijkheid,
    summarize_by_counterparty_per_month,
    summarize_monthly_totals,
    summarize_monthly_totals_by_label,
)
from visualization import plot_counterparty_netto, plot_monthly_overview
from utils import format_month
from label_db import get_labels, save_label, init_db

st.set_page_config(page_title="Financieel Overzicht", layout="wide")


def main():
    init_db()
    st.title("Financieel Overzicht")

    df = clean_transactions(load_csvs("data"))
    summary_df = summarize_by_counterparty_per_month(df)
    summary_df["Maand_NL"] = summary_df["Maand"].apply(format_month)
    summary_df = summary_df.sort_values(by=["Maand", "Netto"], ascending=[True, False])

    label_df = get_labels()
    summary_df = summary_df.merge(label_df, on="Tegenpartij", how="left")

    months = summary_df.drop_duplicates("Maand")[["Maand", "Maand_NL"]].sort_values(
        "Maand"
    )
    month_names = months["Maand_NL"].tolist()
    selected_month = st.selectbox("Filter op maand", ["Alle maanden"] + month_names)

    if selected_month == "Alle maanden":
        filtered_df = summary_df
    else:
        maand_val = months[months["Maand_NL"] == selected_month]["Maand"].iloc[0]
        filtered_df = summary_df[summary_df["Maand"] == maand_val]

    st.subheader(f"Netto per tegenpartij voor {selected_month}")
    st.dataframe(
        filtered_df[["Tegenpartij", "Netto", "Label", "Zakelijk"]].style.format(
            {"Netto": "{:,.2f}"}
        )
    )

    tab1, tab2, tab3 = st.tabs(
        ["Per Tegenpartij", "Maandelijkse Samenvatting", "Tegenpartij Labels"]
    )

    with tab1:
        if selected_month != "Alle maanden":
            fig = plot_counterparty_netto(filtered_df)
            st.pyplot(fig)
        else:
            st.info(
                "Selecteer een specifieke maand om de grafiek per tegenpartij te zien."
            )

    with tab2:
        zakelijkheid = st.selectbox(
            "Filter op zakelijkheid", ["Alle", "Zakelijk", "Niet-zakelijk"], index=0
        )

        filtered_label_df = filter_zakelijkheid(summary_df, zakelijkheid)

        monthly = summarize_monthly_totals_by_label(filtered_label_df)

        fig2 = plot_monthly_overview(monthly)
        st.pyplot(fig2)

    with tab3:
        st.subheader("Tegenpartij Labels")
        all_parties = sorted(summary_df["Tegenpartij"].unique())
        labels_df = get_labels()

        for tp in all_parties:
            existing = labels_df[labels_df["Tegenpartij"] == tp]
            col1, col2 = st.columns([3, 3])

            col1, col2, col3 = st.columns([2, 5, 3])

            with col1:
                col1.write(tp)
            with col2:
                label = st.text_input(
                    f"Label voor {tp}",
                    value=existing["Label"].values[0] if not existing.empty else "",
                    key=f"label_{tp}",
                    label_visibility="collapsed",
                )
            with col3:
                zakelijk = st.selectbox(
                    "Zakelijkheid",
                    ["Zakelijk", "Niet-zakelijk"],
                    index=(
                        0
                        if not existing.empty and existing["Zakelijk"].values[0]
                        else 1
                    ),
                    key=f"zakelijk_{tp}",
                    label_visibility="collapsed",
                )

            label_changed = not existing.empty and label != existing["Label"].values[0]
            zakelijk_changed = (
                not existing.empty
                and (zakelijk == "Zakelijk") != existing["Zakelijk"].values[0]
            )
            is_new_entry = existing.empty and (label or zakelijk)

            if label_changed or zakelijk_changed or is_new_entry:
                save_label(tp, label, zakelijk == "Zakelijk")


if __name__ == "__main__":
    main()
