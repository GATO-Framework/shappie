import datetime

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


def get_message_statistics(start_time: datetime.datetime, end_time: datetime.datetime):
    start = start_time.isoformat()
    end = end_time.isoformat()
    query = f"""
    {{
      messageStatistics(startTime: "{start}", endTime: "{end}") {{
        timePeriod
        numMessages
      }}
    }}
    """
    response = _send_graphql_request(query)
    data = response["data"]
    streamlit.code(data)
    return [
        {"time_period": stat["timePeriod"], "num_messages": stat["numMessages"]}
        for stat in data["messageStatistics"]
    ]


def main():
    streamlit.title("Shappie Dashboard")

    personas = get_personas()
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

    # Display message statistics
    message_statistics = get_message_statistics(
        start_time=datetime.datetime.now() - datetime.timedelta(days=3),
        end_time=datetime.datetime.now(),
    )
    if message_statistics:
        streamlit.subheader("Message Statistics")
        streamlit.dataframe(message_statistics)
    else:
        streamlit.warning("No message statistics available.")


if __name__ == '__main__':
    main()
