from ddgs import DDGS
import requests
from bs4 import BeautifulSoup


def web_search(query: str, max_results: int = 5):
    results = []

    latest_keywords = [
        "latest",
        "recent",
        "current",
        "today",
        "2026",
        "2025",
        "this year",
        "new developments",
    ]

    is_latest_query = any(
        keyword in query.lower()
        for keyword in latest_keywords
    )

    last_error = None

    # Try the search up to 3 times
    for attempt in range(3):
        try:
            print("================================")
            print(f"DDGS SEARCH ATTEMPT {attempt + 1}/3")
            print("Query:", query)
            print("================================")

            with DDGS(timeout=20) as ddgs:

                search_results = ddgs.text(
    query,
    max_results=max_results,
    timelimit="y" if is_latest_query else None,
    backend="google,brave,bing,duckduckgo",
)

                for result in search_results:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                    })

            # Search completed successfully
            print("DDGS SEARCH SUCCESS")
            print("Results found:", len(results))

            return results

        except Exception as e:
            last_error = e

            print("================================")
            print("DDGS SEARCH ERROR")
            print("Attempt:", attempt + 1)
            print("Query:", query)
            print("Error:", repr(e))
            print("================================")

    # All 3 attempts failed
    raise RuntimeError(
        f"Search service failed after 3 attempts: {str(last_error)}"
    ) from last_error

def fetch_page(url: str):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
        ]):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True,
        )

        return text[:10000]

    except Exception as e:
        return f"Could not fetch page: {str(e)}"