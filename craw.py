import json
import time

from bs4 import BeautifulSoup
from requests import get as http_get


def get_page(url: str, params={}) -> BeautifulSoup:
    response = http_get(url, params=params, headers={"User-Agent": "Firefox"})
    if response.status_code != 200:
        raise Exception("page not found! " + response.status)
    return BeautifulSoup(response.content.decode("utf-8"), "html.parser")


def get_tender(year: int) -> list:
    def clear_text(text: str) -> str:
        old = text
        new = text.replace("\n", " ").replace("  ", " ")
        while old != new:
            old = new
            new = old.replace("  ", " ")
        return new

    page = 1
    result = []
    while True:
        print(f"Obtendo página N° {page}...")
        soup = get_page(
            "https://transparencia.jurema.pi.gov.br/jurema/licitacoes",
            {"ano": year, "page": page},
        )
        table = soup.find(
            "table", class_="table table-striped table-hover table-sm tablesize"
        )
        if not table:
            print("Página vazia, terminou!")
            break
        for t in table.find("tbody").find_all("tr"):
            columns = t.find_all("td")
            item = {
                "n_procedimento": columns[0].text.strip(),
                "procedimento": clear_text(columns[1].text.strip()),
                "tipo_licitacao": columns[2].text.strip(),
                "objeto": columns[3].text.strip(),
                "processo": columns[4].text.strip(),
                "situacao": columns[5].text.strip(),
                "data_abertura": columns[6].text.strip(),
                "valor_previsto": columns[7].text.strip(),
                "valor_homologado": columns[8].text.strip(),
                "ano": year,
            }
            result.append(item)
        page += 1
    return result


data = []
for year in range(2013, time.gmtime().tm_year + 1):
    print(f"Obtendo do ano {year}...")
    data += get_tender(year)
json.dump(data, open("tenders.json", "w"), indent=2, ensure_ascii=False)
