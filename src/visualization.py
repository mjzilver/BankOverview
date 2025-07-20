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
    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(monthly))
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
            xytext=(0, 3 if height > 0 else -10),
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
    return fig
