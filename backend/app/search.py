from ddgs import DDGS
import requests
from bs4 import BeautifulSoup


def web_search(query: str, max_results: int = 5):
    results = []

    # Detect questions where freshness matters
    latest_keywords = [
        "latest", "recent", "current", "today",
        "2026", "2025", "this year", "new developments"
    ]

    is_latest_query = any(
        keyword in query.lower()
        for keyword in latest_keywords
    )

    with DDGS() as ddgs:

        if is_latest_query:
            search_results = ddgs.text(
                query,
                max_results=max_results,
                timelimit="y"
            )
        else:
            search_results = ddgs.text(
                query,
                max_results=max_results
            )

        for result in search_results:
            results.append({
                "title": result.get("title"),
                "url": result.get("href"),
                "snippet": result.get("body")
            })

    return results


def fetch_page(url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove unnecessary elements
        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header"
        ]):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        return text[:10000]

    except Exception as e:
        return f"Could not fetch page: {str(e)}"