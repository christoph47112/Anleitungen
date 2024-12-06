import sqlite3
import streamlit as st
from rapidfuzz import process, fuzz
import PyPDF2
import os

# Datenbankpfad
DATABASE = '/mnt/data/expanded_instructions_database.db'

# Sicherstellen, dass der Upload-Ordner existiert
UPLOAD_FOLDER = os.path.abspath('./uploaded_pdfs')
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except FileExistsError:
    pass

# Funktion: Beispielanleitungen zur Datenbank hinzufügen
def add_example_instructions():
    """Fügt Beispielanleitungen zur SQLite-Datenbank hinzu."""
    example_instructions = [
        {
            "title": "Wie lege ich eine Aktion an?",
            "content": "1. Gehen Sie zu 'Stammdaten' -> 'Aktionen'.
2. Klicken Sie auf 'Neue Aktion anlegen'.
3. Geben Sie die Aktionsdaten wie Name, Zeitraum und Märkte ein.
4. Fügen Sie Artikel hinzu, die in der Aktion enthalten sein sollen.
5. Speichern Sie die Aktion."
2. Klicken Sie auf 'Neue Aktion anlegen'.
3. Geben Sie die Aktionsdaten wie Name, Zeitraum und Märkte ein.
4. Fügen Sie Artikel hinzu, die in der Aktion enthalten sein sollen.
5. Speichern Sie die Aktion."
2. Klicken Sie auf 'Neue Aktion anlegen'.
3. Geben Sie die Aktionsdaten wie Name, Zeitraum und Märkte ein.
4. Fügen Sie Artikel hinzu, die in der Aktion enthalten sein sollen.
5. Speichern Sie die Aktion."


2. Klicken Sie auf 'Neue Aktion anlegen'.

3. Geben Sie die Aktionsdaten wie Name, Zeitraum und Märkte ein.

4. Fügen Sie Artikel hinzu, die in der Aktion enthalten sein sollen.

5. Speichern Sie die Aktion.
",
            "pdf_path": ""
        },
        {
            "title": "Wie kann ich Artikel zu einer bestehenden Aktion hinzufügen?",
            "content": "1. Gehen Sie zu 'Stammdaten' -> 'Aktionen'.
2. Wählen Sie die Aktion aus, zu der Sie Artikel hinzufügen möchten.
3. Klicken Sie auf 'Artikel hinzufügen'.
4. Geben Sie die Artikelnummer oder den Namen des Artikels ein.
5. Speichern Sie die Änderungen."
3. Klicken Sie auf 'Artikel hinzufügen'.
4. Geben Sie die Artikelnummer oder den Namen des Artikels ein.
5. Speichern Sie die Änderungen."
3. Klicken Sie auf 'Artikel hinzufügen'.
4. Geben Sie die Artikelnummer oder den Namen des Artikels ein.
5. Speichern Sie die Änderungen."
3. Klicken Sie auf 'Artikel hinzufügen'.
4. Geben Sie die Artikelnummer oder den Namen des Artikels ein.
5. Speichern Sie die Änderungen.",
            "pdf_path": ""
        },
        {
            "title": "Wie aktiviere oder deaktiviere ich eine Aktion?",
            "content": "1. Gehen Sie zu 'Stammdaten' -> 'Aktionen'.
2. Wählen Sie die Aktion aus, die Sie aktivieren oder deaktivieren möchten.
3. Klicken Sie auf 'Aktion aktivieren' oder 'Aktion deaktivieren'.
4. Bestätigen Sie die Änderung und speichern Sie."
3. Klicken Sie auf 'Aktion aktivieren' oder 'Aktion deaktivieren'.
4. Bestätigen Sie die Änderung und speichern Sie."
3. Klicken Sie auf 'Aktion aktivieren' oder 'Aktion deaktivieren'.
4. Bestätigen Sie die Änderung und speichern Sie."
3. Klicken Sie auf 'Aktion aktivieren' oder 'Aktion deaktivieren'.
4. Bestätigen Sie die Änderung und speichern Sie.",
            "pdf_path": ""
        }
    ]
    conn = get_connection()
    cursor = conn.cursor()
    for instruction in example_instructions:
        cursor.execute("INSERT INTO instructions (title, content, pdf_path) VALUES (?, ?, ?)", (instruction["title"], instruction["content"], instruction["pdf_path"]))
    conn.commit()
    conn.close()

# Funktion: Verbindung zur Datenbank herstellen
def get_connection():
    """Stellt eine Verbindung zur SQLite-Datenbank her."""
    conn = sqlite3.connect(DATABASE)
    # Sicherstellen, dass die Tabelle existiert
    conn.execute('''CREATE TABLE IF NOT EXISTS instructions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        pdf_path TEXT NOT NULL
                    )''')
    conn.commit()
    return conn

# Funktion: Neue Anleitung zur Datenbank hinzufügen
def add_instruction(title, content, pdf_path):
    """Fügt eine neue Anleitung zur SQLite-Datenbank hinzu."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO instructions (title, content, pdf_path) VALUES (?, ?, ?)", (title, content, pdf_path))
    conn.commit()
    conn.close()

# Funktion: Neue Anleitungen aus PDF-Dateien hinzufügen
def add_instructions_from_pdfs(pdf_files):
    """Fügt neue Anleitungen aus einer Liste von PDF-Dateien zur SQLite-Datenbank hinzu."""
    for pdf_file in pdf_files:
        # Speichern der PDF-Datei
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.name)
        if os.path.exists(pdf_path):
            base, extension = os.path.splitext(pdf_file.name)
            counter = 1
            while os.path.exists(pdf_path):
                pdf_path = os.path.join(UPLOAD_FOLDER, f"{base}_{counter}{extension}")
                counter += 1
        if os.path.isdir(UPLOAD_FOLDER):
            with open(pdf_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            f.write(pdf_file.getbuffer())

        # PDF-Inhalt extrahieren
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        content = ""
        for page in pdf_reader.pages:
            content += page.extract_text() + "\n"

        # Titel automatisch aus dem Dateinamen generieren
        title = os.path.splitext(pdf_file.name)[0]

        # Zusammenfassung und Schritt-für-Schritt-Anleitung erstellen
        summary, steps = generate_summary_and_steps(content)
        structured_content = f"### Zusammenfassung\n{summary}\n\n### Schritt-für-Schritt-Anleitung\n{steps}"

        # Anleitung zur Datenbank hinzufügen
        add_instruction(title, structured_content, pdf_path)

# Funktion: Generiert eine Zusammenfassung und eine Schritt-für-Schritt-Anleitung
def generate_summary_and_steps(content):
    """Erstellt eine Zusammenfassung und eine Schritt-für-Schritt-Anleitung basierend auf dem PDF-Inhalt."""
    # Hier wird eine einfache Heuristik verwendet, um die wichtigsten Inhalte zusammenzufassen
    lines = content.split("\n")
    summary = "".join(lines[:3])  # Nimmt die ersten 3 Zeilen als Zusammenfassung (kann angepasst werden)
    steps = "\n".join([f"- {line}" for line in lines if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '•', '-'))])
    return summary, steps

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
    if not titles:
        return []
    
    matches = process.extract(
        query,
        [row[0] + " " + row[1] for row in titles],
        limit=5,
        scorer=fuzz.partial_ratio
    )

    # Ergebnisse filtern
    filtered_results = [titles[matches[idx][2]] for idx in range(len(matches)) if matches[idx][1] > 0]
    return filtered_results

add_example_instructions()

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
                    with st.expander("Anleitung anzeigen", expanded=True):
                        st.markdown(content, unsafe_allow_html=True)
                    if pdf_path and os.path.isfile(pdf_path):
                        with open(pdf_path, 'rb') as pdf_file:
                            pdf_bytes = pdf_file.read()
                        st.download_button(label="PDF herunterladen", data=pdf_bytes, file_name=os.path.basename(pdf_path), mime="application/pdf")
                    else:
                        st.warning("PDF-Datei nicht gefunden.")
            else:
                st.write("Keine Ergebnisse gefunden.")
        except Exception as e:
            st.error(f"Fehler bei der Suche: {str(e)}")

        # Zurücksetzen der Suche
        if st.button("Suche zurücksetzen"):
            query = ""

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
            with st.expander("Anleitung anzeigen", expanded=True):
                st.markdown(result[0], unsafe_allow_html=True)
            if result[1] and os.path.isfile(result[1]):
                with open(result[1], 'rb') as pdf_file:
                    pdf_bytes = pdf_file.read()
                st.download_button(label="PDF herunterladen", data=pdf_bytes, file_name=os.path.basename(result[1]), mime="application/pdf")
            

# Tab 3: Anleitung hinzufügen
with tab3:
    st.subheader("Neue Anleitungen hinzufügen")
    new_pdf_files = st.file_uploader("PDF-Dateien der Anleitungen hochladen", type=["pdf"], accept_multiple_files=True)

    if st.button("Anleitungen speichern"):
        if new_pdf_files:
            try:
                add_instructions_from_pdfs(new_pdf_files)
                st.success("Anleitungen erfolgreich hinzugefügt.")
            except Exception as e:
                st.error(f"Fehler beim Hinzufügen der Anleitungen: {str(e)}")
        else:
            st.error("Bitte wählen Sie mindestens eine PDF-Datei aus.")
