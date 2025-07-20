import streamlit as st
from data_loader import load_csvs, clean_transactions, merge_and_clean_labels
from analysis import (
    filter_zakelijkheid,
    summarize_by_counterparty_per_month,
    summarize_monthly_totals_by_label,
)
import settings
from visualization import (
    plot_counterparty_netto,
    plot_label_netto,
    plot_monthly_overview,
)
from utils import format_month
from label_db import get_labels, save_label, init_db

st.set_page_config(page_title="Financieel Overzicht", layout="wide")


def get_selected_month(summary_df):
    months = summary_df.drop_duplicates("Maand")[["Maand", "Maand_NL"]].sort_values(
        "Maand"
    )
    month_names = months["Maand_NL"].tolist()
    selected = st.selectbox("Filter op maand", ["Alle maanden"] + month_names)
    if selected == "Alle maanden":
        return summary_df, selected
    maand_val = months[months["Maand_NL"] == selected]["Maand"].iloc[0]
    return summary_df[summary_df["Maand"] == maand_val], selected


def show_label_editor(summary_df):
    st.subheader("Tegenpartij Labels")
    all_parties = sorted(summary_df["Tegenpartij"].str.strip().unique())
    labels_df = get_labels()

    for tp in all_parties:
        existing = labels_df[labels_df["Tegenpartij"] == tp]

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
                index=0 if not existing.empty and existing["Zakelijk"].values[0] else 1,
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


def main():
    init_db()
    st.title("Financieel Overzicht")

    df = clean_transactions(load_csvs(settings.DATA_DIR))
    summary_df = summarize_by_counterparty_per_month(df)
    summary_df["Maand_NL"] = summary_df["Maand"].apply(format_month)
    summary_df = summary_df.sort_values(by=["Maand", "Netto"], ascending=[True, False])

    summary_df = merge_and_clean_labels(summary_df, get_labels())

    filtered_df, selected_month = get_selected_month(summary_df)

    # Tables
    tab_table1, tab_table2 = st.tabs(["Tegenpartij Netto", "Label Netto"])
    with tab_table1:
        st.subheader(f"Netto per tegenpartij voor {selected_month}")
        st.dataframe(
            filtered_df[["Tegenpartij", "Netto", "Label", "Zakelijk_NL"]].style.format(
                {"Netto": "{:,.2f}"}
            )
        )

    with tab_table2:
        st.subheader(f"Netto per label voor {selected_month}")
        grouped = (
            filtered_df.groupby(["Label", "Zakelijk_NL"], as_index=False)["Netto"]
            .sum()
            .sort_values(by="Netto", ascending=False)
        )
        st.dataframe(grouped.style.format({"Netto": "{:,.2f}"}))

    # Graphs + Input
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Per Tegenpartij",
            "Per Label",
            "Maandelijkse Samenvatting",
            "Tegenpartij Labels",
        ]
    )

    with tab1:
        if selected_month != "Alle maanden":
            st.pyplot(plot_counterparty_netto(filtered_df))
        else:
            st.info(
                "Selecteer een specifieke maand om de grafiek per tegenpartij te zien."
            )

    with tab2:
        if selected_month != "Alle maanden":
            st.pyplot(plot_label_netto(filtered_df))
        else:
            st.info("Selecteer een specifieke maand om de grafiek per label te zien.")

    with tab3:
        zakelijkheid = st.selectbox(
            "Filter op zakelijkheid", ["Alle", "Zakelijk", "Niet-zakelijk"], index=0
        )
        filtered_label_df = filter_zakelijkheid(summary_df, zakelijkheid)
        monthly = summarize_monthly_totals_by_label(filtered_label_df)
        st.pyplot(plot_monthly_overview(monthly))

    with tab4:
        show_label_editor(summary_df)


if __name__ == "__main__":
    main()
