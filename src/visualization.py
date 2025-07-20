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


def plot_monthly_overview(monthly):
    fig, ax = plt.subplots(figsize=(12, 5))

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
        uitgaven = subset["uitgaven"].values

        ax.bar(x, inkomsten, width=width / 2, bottom=income_bottom,
               label=f"In: {label}", color=label_colors[label])
        ax.bar(x + width / 2, uitgaven, width=width / 2, bottom=expense_bottom,
               label=f"Uit: {label}", color=label_colors[label])

        income_bottom += inkomsten
        expense_bottom += uitgaven

    ax.set_ylabel("Bedrag (€)")
    ax.set_xticks(x + width / 4)
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.legend(title="Labelkleur en soort", bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.set_title("Maandelijkse Inkomsten/Uitgaven per Label")
    plt.tight_layout()
    return fig
