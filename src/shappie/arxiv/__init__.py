import requests
import urllib.parse
import xml.etree.ElementTree as ET
import json
import pathlib
from random import choice
import asyncio

path = pathlib.Path(__file__).parent / "result_response.json"
with open(path) as file:
    response_options = json.load(file)


async def search(query):
    url = f'http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&start=0&max_results=5'
    # response = requests.get(url) RUN ASYNC
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, url)
    response.raise_for_status()  # Raise exception if the request failed

    root = ET.fromstring(response.content)

    entries = root.findall('{http://www.w3.org/2005/Atom}entry')
    results = []

    for entry in entries:
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        published = entry.find('{http://www.w3.org/2005/Atom}published').text
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
        link = entry.find("{http://www.w3.org/2005/Atom}link[@title='doi']")
        arxiv_link = entry.find(
            "{http://www.w3.org/2005/Atom}id").text
        doi = link.get('href') if link is not None else None

        results.append({
            'title': title,
            'published': published,
            'summary': summary,
            'doi': doi,
            'arxiv_link': arxiv_link
        })

    return results


def format_results(results):
    formatted_results = []
    for i, result in enumerate(results):
        formatted_results.append(
            f'{i + 1}. {result["title"]} (<{result["arxiv_link"]}>)')
    response = '\n'.join(formatted_results)
    return choice(response_options) + response
