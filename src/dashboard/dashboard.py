import collections
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


@streamlit.cache_data
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

    counts: dict[datetime.date, int] = collections.defaultdict(int)

    # Compute sums for each day
    for stat in statistics:
        date = datetime.date(stat["year"], stat["month"], stat["day"])
        counts[date] += stat["numMessages"]

    # Today's total messages
    today = datetime.date.today()
    today_messages = counts[today]
    yesterday_messages = counts[today - datetime.timedelta(days=1)]

    # This week's total messages
    week_start = today - datetime.timedelta(days=6)
    this_week_messages = sum(
        counts[date] for date in counts if week_start <= date <= today)
    last_week_start = week_start - datetime.timedelta(days=7)
    last_week_messages = sum(
        counts[date] for date in counts if last_week_start <= date < week_start)

    # Past 30 days' total messages
    last_month_messages = sum(
        counts[date] for date in counts if start_time.date() <= date <= today)

    return dict(
        today=today_messages,
        today_change=today_messages - yesterday_messages,
        week=this_week_messages,
        week_change=this_week_messages - last_week_messages,
        month=last_month_messages,
    )


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

    streamlit.subheader("Message Statistics")

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
    else:
        streamlit.warning("No message statistics available.")


if __name__ == '__main__':
    main()
