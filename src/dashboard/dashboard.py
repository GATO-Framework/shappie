import streamlit

import datastore


def main():
    streamlit.title("Shappie Dashboard")

    url = streamlit.text_input("Database URL")
    store = datastore.DataStore(url, "GATO")
    personas = store.list_personas()
    p = personas[0]
    name = streamlit.selectbox("Personas", [])
    description = streamlit.text_area("Persona Description")


if __name__ == '__main__':
    main()
