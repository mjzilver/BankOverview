import streamlit as st
from data_loader import load_csvs, clean_transactions
from analysis import summarize_by_counterparty_per_month, summarize_monthly_totals
from visualization import plot_counterparty_netto, plot_monthly_overview
from utils import format_month

st.set_page_config(page_title="Financieel Overzicht", layout="wide")


def main():
    st.title("Financieel Overzicht")

    df = clean_transactions(load_csvs("data"))
    summary_df = summarize_by_counterparty_per_month(df)
    summary_df["Maand_NL"] = summary_df["Maand"].apply(format_month)
    summary_df = summary_df.sort_values(by=["Maand", "Netto"], ascending=[True, False])

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
        filtered_df[["Tegenpartij", "Netto"]].style.format({"Netto": "{:,.2f}"})
    )

    tab2, tab1 = st.tabs(["Maandelijkse Samenvatting", "Per Tegenpartij"])

    with tab2:
        monthly = summarize_monthly_totals(summary_df)
        fig2 = plot_monthly_overview(monthly)
        st.pyplot(fig2)

    with tab1:
        if selected_month != "Alle maanden":
            fig = plot_counterparty_netto(filtered_df)
            st.pyplot(fig)
        else:
            st.info(
                "Selecteer een specifieke maand om de grafiek per tegenpartij te zien."
            )


if __name__ == "__main__":
    main()
