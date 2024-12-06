import streamlit as st
from fuzzywuzzy import process  # Oder verwenden Sie `rapidfuzz`, falls bevorzugt

# Dummy-Daten für `titles`. Ersetzen Sie dies durch Ihre echte Datenquelle.
# titles ist eine Liste von Listen oder Tupeln, z. B. [["Artikel 1", "Beschreibung"], ["Artikel 2", "Details"]]
titles = []

def load_data():
    """Funktion zum Laden von Beispieldaten. Ersetzen Sie dies durch Ihren Dateneingabeprozess."""
    global titles
    # Beispiel: titles aus einer Datei laden
    try:
        # Hier könnte ein Ladevorgang für eine Datei oder Datenbank stehen
        titles = [["Artikel 1", "Beschreibung"], ["Artikel 2", "Details"]]
    except Exception as e:
        st.error("Fehler beim Laden der Daten: " + str(e))
        titles = []

def search_instructions(query):
    """Suchfunktion, die mit fuzzy matching Anweisungen sucht."""
    if not titles:
        raise ValueError("Titles ist leer oder wurde nicht geladen.")
    
    try:
        matches = process.extract(
            query,
            [row[0] + " " + row[1] for row in titles if len(row) > 1],
            limit=5,
            scorer=process.fuzz.partial_ratio
        )
        return matches
    except Exception as e:
        print("Error while processing search_instructions:", str(e))
        raise

# Streamlit App
def main():
    st.title("Anweisungs-Suchtool")
    st.write("Laden Sie Ihre Daten und starten Sie die Suche.")
    
    # Daten laden
    if st.button("Daten laden"):
        load_data()
        st.success("Daten erfolgreich geladen.")
    
    # Sucheingabe
    query = st.text_input("Geben Sie eine Suche ein:")
    if query:
        try:
            results = search_instructions(query)
            st.write("Suchergebnisse:")
            for result in results:
                st.write(f"Match: {result[0]} - Score: {result[1]}")
        except Exception as e:
            st.error(f"Fehler bei der Suche: {str(e)}")

if __name__ == "__main__":
    main()
