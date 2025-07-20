from matplotlib import cm
from matplotlib.colors import to_hex
import matplotlib.pyplot as plt
import numpy as np


def plot_counterparty_netto(filtered_df):
    n_rows = len(filtered_df)
    fig_height = max(4, n_rows * 0.1)
    fig, ax = plt.subplots(figsize=(8, fig_height))

    colors = filtered_df["Netto"].apply(lambda x: "green" if x >= 0 else "red")
    bars = ax.barh(
        filtered_df["Tegenpartij"][::-1], filtered_df["Netto"][::-1], color=colors[::-1]
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
            fontsize=6,
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
            fontsize=6,
            color="black",
        )

    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()
    return fig


def plot_label_netto(filtered_df):
    filtered_df = filtered_df.copy()
    filtered_df["Label"] = filtered_df["Label"].replace("", "geen label")
    filtered_df = filtered_df.sort_values(by=["Label", "Netto"], ascending=[True, False])

    grouped = filtered_df.groupby("Label")
    agg_df = grouped.agg(
        Netto=("Netto", "sum"),
        Positief=("Netto", lambda x: (x > 0).sum()),
        Negatief=("Netto", lambda x: (x < 0).sum()),
        Aantal=("Tegenpartij", "count"),
    ).reset_index()
    filtered_df = agg_df
    
    n_rows = len(filtered_df)
    fig_height = max(4, n_rows * 0.1)
    fig, ax = plt.subplots(figsize=(8, fig_height))

    colors = filtered_df["Netto"].apply(lambda x: "green" if x >= 0 else "red")
    bars = ax.barh(
        filtered_df["Label"][::-1], filtered_df["Netto"][::-1], color=colors[::-1]
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
            fontsize=6,
            color="black",
        )

        label_text = filtered_df["Label"].iloc[::-1].iloc[i]
        ax.annotate(
            label_text[:50],
            xy=(0, y),
            xytext=(-offset if width >= 0 else offset, 0),
            textcoords="offset points",
            ha="right" if width >= 0 else "left",
            va="center",
            fontsize=6,
            color="black",
        )

    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()
    return fig


def plot_monthly_overview(monthly):
    fig, ax = plt.subplots(figsize=(12, 5))
    
    monthly["Label"] = monthly["Label"].replace("", "geen label")

    months = monthly["Maand_NL"].unique()
    labels = monthly["Label"].unique()
    
    x = np.arange(len(months))
    width = 0.8

    cmap = cm.get_cmap("tab20", len(labels))
    label_colors = {label: to_hex(cmap(i)) for i, label in enumerate(labels)}

    income_bottom = np.zeros(len(months))
    expense_bottom = np.zeros(len(months))

    for label in labels:
        subset = monthly[monthly["Label"] == label]
        subset = subset.set_index("Maand_NL").reindex(months, fill_value=0)

        inkomsten = subset["inkomsten"].values
        uitgaven = subset["uitgaven"].abs().values

        ax.bar(
            x,
            inkomsten,
            width=width / 3,
            bottom=income_bottom,
            label=label,
            color=label_colors[label],
        )
        ax.bar(
            x + width / 3,
            uitgaven,
            width=width / 3,
            bottom=expense_bottom,
            label=None,
            color=label_colors[label],
            hatch="/",
        )


        income_bottom += inkomsten
        expense_bottom += uitgaven
        
        
    netto = income_bottom - expense_bottom
    total_bar = ax.bar(
        x + width *2 / 3,
        netto,
        width=width / 3,
        color="gray",
        alpha=0.5,
        label="Netto totaal",
        zorder=3,
    )
    for i, bar in enumerate(total_bar):
        ax.annotate(
            f"{netto[i]:,.2f}€",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 3 if netto[i] >= 0 else -9),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            color="black",
        )

    ax.set_ylabel("Bedrag (€)")
    ax.set_xticks(x + width / 4)
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.legend(title="Labelkleur en soort", bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.set_title("Maandelijkse Inkomsten/Uitgaven per Label")
    plt.tight_layout()
    return fig
