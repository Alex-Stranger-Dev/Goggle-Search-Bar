from flask import Flask, request, render_template_string, Response
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

# šablona s formulářem pro zadání klíčového slova
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Search</title>
    <style>
    body {
        background-color: #F0EAD6; 
        margin-left: 3rem;
        margin-top: 2rem;
        width: 100%;
        hight: 100svh;
        }  
    h1 {
        font-size: 2rem;
    }
    form {
            margin-top: 2rem;
        }
    </style>
</head>
<body>

    <h1>Google Search</h1>
    <form id="searchForm">
        <input type="text" id="query" placeholder="Enter search query">
        <button type="submit">Search</button>
    </form>
    <pre id="results"></pre>

    <script>
        document.getElementById('searchForm').addEventListener('submit', async function(event) {
            event.preventDefault(); // Zabraňuje odeslání formuláře

            const query = document.getElementById('query').value;
            const response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });

            const results = await response.json();
            document.getElementById('results').innerHTML = JSON.stringify(results, null, 2); // Uložení výsledků do souboru
            
            const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'results.json';
            link.click();
        });
    </script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(html_template, results="")


@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query")
    search_url = f"https://www.google.com/search?q={query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for g in soup.find_all("div", class_="g"):
        title = g.find("h3").text if g.find("h3") else ""
        link = g.find("a")["href"] if g.find("a") else ""
        snippet = (
            g.find("span", class_="aCOpRe").text
            if g.find("span", class_="aCOpRe")
            else ""
        )
        results.append({"title": title, "link": link, "snippet": snippet})

    return Response(json.dumps(results), mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)
