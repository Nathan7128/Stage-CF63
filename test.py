import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import mplcursors

# Création d'un DataFrame d'exemple
data = {
    'shooter': ['Player 1', 'Player 2', 'Player 3'],
    'team': ['Team A', 'Team B', 'Team A'],
    'x_start': [30, 40, 50],
    'y_start': [20, 60, 40],
    'x_end': [60, 55, 70],
    'y_end': [45, 80, 60]
}

df = pd.DataFrame(data)

# Création du terrain avec mplsoccer
pitch = Pitch(line_color='black')
fig, ax = pitch.draw(figsize=(10, 7))

# Ajout des flèches pour chaque tir
for idx, row in df.iterrows():
    ax.annotate("", xy=(row['x_end'], row['y_end']), xytext=(row['x_start'], row['y_start']),
                arrowprops=dict(arrowstyle="->", color="blue", lw=2))

# Ajout des info-bulles avec mplcursors
cursor = mplcursors.cursor(hover=True)

@cursor.connect("add")
def on_add(sel):
    idx = sel.index
    row = df.iloc[idx]
    sel.annotation.set_text(f"{row['shooter']} ({row['team']})\n"
                            f"Start: ({row['x_start']}, {row['y_start']})\n"
                            f"End: ({row['x_end']}, {row['y_end']})")

# Affichage du graphique dans Streamlit
plt.show()

st.pyplot(fig)
