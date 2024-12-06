import sqlite3
import streamlit as st
from rapidfuzz import process, fuzz
import PyPDF2
import os

# Datenbankpfad
DATABASE = 'instructions_database.db'

# Funktion: Verbindung zur Datenbank herstellen
def get_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

# Funktion: Suche in der Datenbank mit unscharfer Suche
def search_instructions(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, content, pdf_path FROM instructions")
    results = cursor.fetchall()
    conn.close()

    # Titel und Inhalte durchsuchen mit unscharfer Suche
    titles = [(row[0], row[1], row[2]) for row in results]
    matches = process.extract(query, [row[0] + " " + row[1] for row in titles], limit=5, scorer=fuzz.partial_ratio)

    # Ergebnisse filtern
    filtered_results = [titles[idx[2]] for idx in matches]
    return filtered_results

# Streamlit-App
st.title("Anleitungsmodul für das WWS")

# Tabs für Suche und Anleitungsauswahl
tab1, tab2 = st.tabs(["🔍 Suche", "📚 Anleitung auswählen"])

with tab1:
    st.subheader("Suche nach Anleitungen")
    query = st.text_input("Frage eingeben", placeholder="z. B. 'Wie lege ich eine Aktion an?'")

    if query:
        st.subheader(f"Suchergebnisse für: {query}")
        
        # Suche ausführen
        results = search_instructions(query)

        if results:
            for i, (title, content, pdf_path) in enumerate(results, 1):
                st.markdown(f"**{i}. {title}**")
                st.write(content)
                st.markdown(f"[PDF herunterladen](./{pdf_path})", unsafe_allow_html=True)
        else:
            st.write("Keine Ergebnisse gefunden.")

        # Zurücksetzen der Suche
        if st.button("Suche zurücksetzen"):
            st.experimental_rerun()

with tab2:
    st.subheader("Anleitung auswählen")
    
    # Dropdown für spezifische Anleitungen
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM instructions")
    titles = [row[0] for row in cursor.fetchall()]
    conn.close()

    selected_instruction = st.selectbox("Wähle eine Anleitung aus:", ["-- Auswahl --"] + titles)
    if selected_instruction != "-- Auswahl --":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content, pdf_path FROM instructions WHERE title = ?", (selected_instruction,))
        result = cursor.fetchone()
        conn.close()

        if result:
            st.markdown(f"### {selected_instruction}")
            st.write(result[0])
            st.markdown(f"[PDF herunterladen](./{result[1]})", unsafe_allow_html=True)
