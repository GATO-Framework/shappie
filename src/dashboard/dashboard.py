import datetime

import httpx as httpx
import pandas
import streamlit


def _send_graphql_request(payload):
    url = 'http://api:8000/graphql'
    headers = {'Content-Type': 'application/json'}
    response = httpx.post(url, headers=headers, json={"query": payload})
    if response.status_code != 200:
        streamlit.error(response.text)
    return response.json()


@streamlit.cache_data(ttl=10)
def get_state():
    query = """
    {
      state {
        mode { name }
        constitutions { name }
        persona { name }
      }
    }
    """
    response = _send_graphql_request(query)
    data = response["data"]
    return data["state"]


def set_state(mode: str, constitutions: list[str], persona: str):
    query = f"""
    mutation {{
      updateState(mode: "{mode}",
                  constitutions: {str(constitutions).replace("'", '"')},
                  persona: "{persona}") {{
        mode {{ name }}
        constitutions {{ name }}
        persona {{ name }}
      }}
    }}
    """
    response = _send_graphql_request(query)
    data = response["data"]
    return data


@streamlit.cache_data(ttl=10)
def get_modes():
    query = """
    {
      modes {
        name
      }
    }
    """
    response = _send_graphql_request(query)
    data = response["data"]
    return [mode["name"] for mode in data["modes"]]


@streamlit.cache_data(ttl=10)
def get_constitutions():
    query = """
    {
      constitutions {
        name
      }
    }
    """
    response = _send_graphql_request(query)
    data = response["data"]
    return [constitution["name"] for constitution in data["constitutions"]]


@streamlit.cache_data(ttl=10)
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


@streamlit.cache_data(ttl=600)
def request_message_statistics(start_time: datetime.datetime,
                               end_time: datetime.datetime):
    start = start_time.isoformat()
    end = end_time.isoformat()
    query = f"""
    {{
      messageStatistics(startTime: "{start}", endTime: "{end}") {{
        year
        month
        day
        numMessages
      }}
    }}
    """
    response = _send_graphql_request(query)
    data = response["data"]
    return data["messageStatistics"]


def get_engagement_metrics(
        start_time: datetime.datetime,
        end_time: datetime.datetime,
):
    statistics = request_message_statistics(
        start_time=start_time,
        end_time=end_time,
    )

    if not statistics:
        return None

    # Create DataFrame from statistics
    df = pandas.DataFrame(statistics)
    df['date'] = pandas.to_datetime(df[['year', 'month', 'day']])
    df.set_index('date', inplace=True)
    df = df.resample('D').sum()  # resample to ensure we have entries for each day

    today = pandas.Timestamp(datetime.datetime.now().date())
    yesterday = today - pandas.DateOffset(days=1)
    week_start = today - pandas.DateOffset(days=6)
    last_week_start = week_start - pandas.DateOffset(days=7)

    return {
        'today': int(df.loc[today, 'numMessages']),
        'today_change': int(df.loc[today, 'numMessages'] -
                            df.loc[yesterday, 'numMessages']),
        'week': int(df.loc[week_start:today, 'numMessages'].sum()),
        'week_change': int(df.loc[week_start:today, 'numMessages'].sum() -
                           df.loc[last_week_start:week_start, 'numMessages'].sum()),
        'month': int(df['numMessages'].sum()),
        'chart_data': df[['numMessages']],
    }


def main():
    streamlit.title("Shappie Dashboard")

    tabs = streamlit.tabs(["Message Statistics", "Application State", "Persona"])

    with tabs[0]:
        start_time = datetime.datetime.now() - datetime.timedelta(days=30)
        end_time = datetime.datetime.now()

        message_statistics = get_engagement_metrics(start_time, end_time)

        if message_statistics:
            cols = streamlit.columns(3)
            with cols[0]:
                streamlit.metric(
                    label="Today's Total Messages",
                    value=message_statistics["today"],
                    delta=message_statistics["today_change"],
                )
            with cols[1]:
                streamlit.metric(
                    label="This Week's Total Messages",
                    value=message_statistics["week"],
                    delta=message_statistics["week_change"],
                )
            with cols[2]:
                streamlit.metric(
                    label="Past 30 Day's Total Messages",
                    value=message_statistics["month"],
                )
            streamlit.line_chart(message_statistics['chart_data'])
        else:
            streamlit.warning("No message statistics available.")

    with tabs[1]:
        state = get_state()

        modes = get_modes()
        mode = streamlit.selectbox("Mode", options=modes,
                                   index=modes.index(state["mode"]["name"]))
        constitutions = streamlit.multiselect(
            "Constitution",
            options=get_constitutions(),
            default=[c["name"] for c in state["constitutions"]],
        )
        personas = get_personas()
        persona_list = list(personas.keys())
        persona = streamlit.selectbox("Persona", options=persona_list,
                                      index=persona_list.index(state["persona"]["name"]))
        if streamlit.button("Update State"):
            set_state(mode, constitutions, persona)

    with tabs[2]:
        persona = streamlit.selectbox("Persona Description", options=personas)
        description = streamlit.text_area(
            "Persona Description",
            value=personas[persona],
            height=200,
        ).replace("\n", " ")
        if streamlit.button("Update"):
            mutation = f"""
            mutation {{
              updatePersona(name: "{persona}", description: "{description}") {{
                name
                description
              }}
            }}
            """
            _send_graphql_request(mutation)
            streamlit.success("Persona updated!")


if __name__ == '__main__':
    main()
