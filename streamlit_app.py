
import sqlite3
import streamlit as st

# Datenbankpfad
DATABASE = 'instructions_database.db'

# Funktion: Verbindung zur Datenbank herstellen
def get_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

# Funktion: Suche in der Datenbank
def search_instructions(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title, content, pdf_path FROM instructions WHERE content LIKE ? OR title LIKE ?",
        (f'%{query}%', f'%{query}%')
    )
    results = cursor.fetchall()
    conn.close()
    return results

# Streamlit-App
st.title("Anleitungsmodul für das WWS")

# Eingabefeld für die Suche
query = st.text_input("Suche nach Anleitungen", placeholder="Frage eingeben, z. B. 'Wie lege ich eine Aktion an?'")

if query:
    st.subheader(f"Suchergebnisse für: {query}")
    
    # Suche ausführen
    results = search_instructions(query)
    
    if results:
        for title, content, pdf_path in results:
            st.markdown(f"### {title}")
            st.write(content)
            st.markdown(f"[PDF herunterladen](./{pdf_path})", unsafe_allow_html=True)
    else:
        st.write("Keine Ergebnisse gefunden.")
else:
    st.write("Bitte gib eine Suchanfrage ein.")
