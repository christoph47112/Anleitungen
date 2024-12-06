import sqlite3
import streamlit as st
from rapidfuzz import process, fuzz
import os

# Datenbankpfad
DATABASE = 'instructions_database.db'

# Funktion: Verbindung zur Datenbank herstellen
def get_connection():
    """Stellt eine Verbindung zur SQLite-Datenbank her."""
    return sqlite3.connect(DATABASE)

# Funktion: Neue Anleitung zur Datenbank hinzufügen
def add_instruction(title, content, pdf_path):
    """Fügt eine neue Anleitung zur SQLite-Datenbank hinzu."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO instructions (title, content, pdf_path) VALUES (?, ?, ?)", (title, content, pdf_path))
    conn.commit()
    conn.close()

# Funktion: Suche in der Datenbank mit unscharfer Suche
def search_instructions(query):
    """Durchsucht die Datenbank mit unscharfer Suche."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, content, pdf_path FROM instructions")
    results = cursor.fetchall()
    conn.close()

    # Titel und Inhalte durchsuchen mit unscharfer Suche
    titles = [(row[0], row[1], row[2]) for row in results]
    matches = process.extract(
        query,
        [row[0] + " " + row[1] for row in titles],
        limit=5,
        scorer=fuzz.partial_ratio
    )

    # Ergebnisse filtern
    filtered_results = [titles[matches[idx][2]] for idx in range(len(matches))]
    return filtered_results

# Streamlit-App
st.title("Anleitungsmodul für das WWS")

# Tabs für Suche, Anleitungsauswahl und Anleitung hinzufügen
tab1, tab2, tab3 = st.tabs(["🔍 Suche", "📚 Anleitung auswählen", "➕ Anleitung hinzufügen"])

# Tab 1: Suche
with tab1:
    st.subheader("Suche nach Anleitungen")
    query = st.text_input("Frage eingeben", placeholder="z. B. 'Wie lege ich eine Aktion an?'")

    if query:
        st.subheader(f"Suchergebnisse für: {query}")
        
        try:
            # Suche ausführen
            results = search_instructions(query)

            if results:
                for i, (title, content, pdf_path) in enumerate(results, 1):
                    st.markdown(f"**{i}. {title}**")
                    st.write(content)
                    if os.path.exists(pdf_path):
                        st.markdown(f"[PDF herunterladen]({pdf_path})", unsafe_allow_html=True)
                    else:
                        st.write("PDF-Datei nicht gefunden.")
            else:
                st.write("Keine Ergebnisse gefunden.")
        except Exception as e:
            st.error(f"Fehler bei der Suche: {str(e)}")

        # Zurücksetzen der Suche
        if st.button("Suche zurücksetzen"):
            st.experimental_rerun()

# Tab 2: Anleitung auswählen
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
            if os.path.exists(result[1]):
                st.markdown(f"[PDF herunterladen]({result[1]})", unsafe_allow_html=True)
            else:
                st.write("PDF-Datei nicht gefunden.")

# Tab 3: Anleitung hinzufügen
with tab3:
    st.subheader("Neue Anleitung hinzufügen")
    new_title = st.text_input("Titel der Anleitung")
    new_content = st.text_area("Inhalt der Anleitung")
    new_pdf_path = st.text_input("Pfad zur PDF-Datei")

    if st.button("Anleitung speichern"):
        if new_title and new_content and new_pdf_path:
            try:
                add_instruction(new_title, new_content, new_pdf_path)
                st.success("Anleitung erfolgreich hinzugefügt.")
            except Exception as e:
                st.error(f"Fehler beim Hinzufügen der Anleitung: {str(e)}")
        else:
            st.error("Bitte alle Felder ausfüllen.")
