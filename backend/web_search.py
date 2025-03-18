# web_search.py

import requests

def search_web(query):
    """
    DuckDuckGo Instant Answer API ile web araması yapar.
    """
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url).json()

        if "AbstractText" in response and response["AbstractText"]:
            return response["AbstractText"]
        elif "RelatedTopics" in response and response["RelatedTopics"]:
            return response["RelatedTopics"][0]["Text"] + " - " + response["RelatedTopics"][0]["FirstURL"]
        else:
            return "No relevant results found."

    except Exception as e:
        return f"Error while searching the web: {str(e)}"
