import httpx as httpx
import streamlit


def _send_graphql_request(payload):
    url = 'http://api:8000/graphql'
    headers = {'Content-Type': 'application/json'}
    response = httpx.post(url, headers=headers, json={"query": payload})
    if response.status_code != 200:
        streamlit.error(response.text)
    return response.json()


def get_personas():
    query = """
    {
      personas {
        name
        description
      }
    }
    """
    response = _send_graphql_request(query)
    data = response["data"]
    return {persona["name"]: persona["description"] for persona in data["personas"]}


def main():
    streamlit.title("Shappie Dashboard")

    personas = get_personas()
    print(personas)
    name = streamlit.selectbox("Personas", options=personas)
    description = streamlit.text_area(
        "Persona Description",
        value=personas[name],
        height=200,
    ).replace("\n", " ")
    if streamlit.button("Update"):
        mutation = f"""
        mutation {{
          updatePersona(name: "{name}", description: "{description}") {{
            name
            description
          }}
        }}
        """
        _send_graphql_request(mutation)
        streamlit.success("Persona updated!")


if __name__ == '__main__':
    main()
