import socket
import requests
from bs4 import BeautifulSoup
import datetime
import yfinance as yf

HOST = 'localhost'
PORT = 9091

# Insert your API keys here
TMDB_API_KEY = 'de3a9cf3e8c995193b73dec220e930f5'         # https://www.themoviedb.org/
NEWSDATA_API_KEY = 'pub_8dc428a72b0f441aba193e0507bf8e5f' # https://newsdata.io/

def get_latest_news():
    """Get latest news headlines using NewsData.io API."""
    url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&country=us&language=en&category=top"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        articles = data.get('results', [])
        if not articles:
            return "📰 No news headlines found."
        headlines = [f"• {a['title']}" for a in articles[:10]]
        return "📰 Latest News Headlines:\n" + "\n".join(headlines)
    except Exception as e:
        return f"❌ Error fetching news: {e}"

def get_today_movies_tmdb(region="US"):
    """Fetches movies released today in the specified region using TMDb API."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "primary_release_date.gte": today,
        "primary_release_date.lte": today,
        "region": region,
        "sort_by": "popularity.desc",
        "language": "en-US",
        "page": 1,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return f"❌ TMDb error: {r.status_code} {r.text}"
        data = r.json()
        results = data.get("results", [])
        if not results:
            return f"🎬 No movies released today found for region {region}."
        response = f"🎬 Movies released today ({today}) in region {region}:\n"
        for movie in results[:10]:  # Show top 10
            title = movie.get("title", "Unknown")
            overview = movie.get("overview", "")
            release_date = movie.get("release_date", "N/A")
            vote_average = movie.get("vote_average", "N/A")
            response += (
                f"\n• {title} (Release: {release_date}, Rating: {vote_average})\n"
                f"  {overview[:150]}{'...' if len(overview) > 150 else ''}\n"
            )
        return response
    except Exception as e:
        return f"❌ Error fetching today's movie releases: {e}"

def wikipedia_search(query):
    """Search Wikipedia and return the summary of the top result."""
    try:
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'format': 'json',
            'utf8': 1,
            'srlimit': 1
        }
        r = requests.get("https://en.wikipedia.org/w/api.php", params=params, timeout=8)
        data = r.json()
        if not data['query']['search']:
            return None
        title = data['query']['search'][0]['title']
        # Get summary
        summary_params = {
            'action': 'query',
            'prop': 'extracts',
            'exintro': True,
            'explaintext': True,
            'titles': title,
            'format': 'json',
            'utf8': 1
        }
        r2 = requests.get("https://en.wikipedia.org/w/api.php", params=summary_params, timeout=8)
        pages = r2.json()['query']['pages']
        summary = next(iter(pages.values()))['extract']
        return f"📚 {title}\n{summary[:800]}{'...' if len(summary) > 800 else ''}"
    except Exception:
        return None

def extract_raw_text(url):
    """Extract readable text from any HTML page."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if "text/html" not in r.headers.get("Content-Type", ""):
            return "⚠️ Non-readable content."
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator="\n").strip()
        return text[:800] + "..." if len(text) > 800 else text
    except Exception as e:
        return f"❌ Error extracting: {e}"

def get_stock_price(symbol):
    """Get the latest stock price using yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if data.empty:
            return f"💹 No data found for symbol '{symbol}'."
        price = data['Close'].iloc[-1]
        return f"💹 {symbol.upper()} Latest Close Price: ${price:.2f}"
    except Exception as e:
        return f"❌ Error fetching stock price: {e}"

def answer_query(query):
    ql = query.lower().strip()
    # Stock price queries
    if ql.startswith("stock "):
        symbol = ql.split("stock ", 1)[1].strip().split()[0].upper()
        return get_stock_price(symbol)
    # News queries
    if "news" in ql or "headline" in ql:
        return get_latest_news()
    # Movie queries
    if "today" in ql and "movie" in ql and "list" in ql:
        return get_today_movies_tmdb(region="US")
    # URL extraction
    for word in query.split():
        if word.startswith("http://") or word.startswith("https://"):
            return extract_raw_text(word)
    # Wikipedia/general knowledge
    wiki_answer = wikipedia_search(query)
    if wiki_answer:
        return wiki_answer
    return "❌ Sorry, I couldn't find an answer. Try rephrasing or providing a specific URL."

def start_server():
    print(f"🟢 MCP Server running on port {PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)
        conn, addr = server.accept()
        print(f"🔌 Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(2048).decode().strip()
                if not data or data.lower() in {"exit", "quit", "shutdown"}:
                    print("🔴 Connection closed.")
                    break
                print(f"📥 Question: {data}")
                response = answer_query(data)
                conn.sendall(response.encode())

if __name__ == "__main__":
    start_server()
