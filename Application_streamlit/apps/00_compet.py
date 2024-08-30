import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(layout = "wide")

def modif_compet(df, compet_SB, compet_SK, i) :
    if compet_SK != "" :
        df = pd.concat([df, df[df.compet_SK == compet_SK].replace(compet_SB, "")])
    # df = df[df.compet_SK != st.session_state[f"{compet_SB}{i}"]]
    df.loc[df.compet_SB == compet_SB, "compet_SK"] = st.session_state[f"{compet_SB}{i}"]
    if st.session_state[f"{compet_SB}{i}"] != "" :
        df.drop(df[(df.compet_SB != compet_SB) & (df.compet_SK == st.session_state[f"{compet_SB}{i}"])].index, inplace = True)
    st.session_state["df_compet"] = df

if "df_compet" not in st.session_state :

    connect = sqlite3.connect("raw-database.db")

    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()

    req = cursor.execute("SELECT * from compet_modif")
    res = req.fetchall()
    desc = req.description
    df = pd.DataFrame(res)
    df.columns = [i[0] for i in desc]
    df.fillna("", inplace = True)

    st.session_state["df_compet"] = df

df = st.session_state["df_compet"]
df.sort_values(by = "compet_SB", inplace = True)

i = 0
for compet_SB, compet_SK, _, _ in df[df.compet_SB != ""].values :
    if i%5 == 0 :
        columns = st.columns(5, gap = "large", vertical_alignment = "bottom")
        st.divider()
    with columns[i%5] :
        st.selectbox(compet_SB, options = pd.Series([compet_SK, ""] + df.loc[df.compet_SB == "", "compet_SK"].tolist()).unique(),
                    index = 0, key = f"{compet_SB}{i}", on_change = modif_compet, args = [df, compet_SB, compet_SK, i])
    i += 1

st.dataframe(df, hide_index = True, height = 600)
