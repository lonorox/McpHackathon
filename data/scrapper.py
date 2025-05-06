import html
import json

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

def extractCharts(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Select chart containers inside the correct structure
    charts = soup.select("div.chart-rows")
    all_charts = []
    if not charts:
        print("No charts found on this page.  " + url)


    for idx, chart_div in enumerate(charts, 1):
        # print(f"\nChart {idx} HTML snippet:\n{chart_div.prettify()[:500]}...")  # limit to 500 chars

        raw_data = chart_div.get("data-chart")
        if not raw_data:
            print(f"Chart {idx} has no data-chart attribute.")
            continue

        try:
            chart_data = json.loads(html.unescape(raw_data))
            # print(url)
            all_charts.append(chart_data)
            # print(f"Chart {idx} parsed data:\n{chart_data}\n")
            return all_charts
        except json.JSONDecodeError as e:
            print(f"Chart {idx} - Failed to parse JSON: {e}")

    # Save the parsed data to a JSON file
    with open("parsed_chart_data.json", "w", encoding="utf-8") as jsonfile:
        json.dump(all_charts, jsonfile, ensure_ascii=False, indent=4)


def extractFolders(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to load {url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    archive_div = soup.find('div', class_='archive-items mb-3')
    urls = [a['href'] for a in archive_div.find_all('a', href=True)]
    return urls

def extract_table_from_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to load {url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    table_div = soup.find("div", class_="value-databases-table")

    if not table_div:
        print(f"No data table found in {url}")
        return None

    table = table_div.find("table")
    if not table:
        print(f"No <table> found inside div for {url}")
        return None

    headers = []
    rows = []

    for tr_index, row in enumerate(table.find_all("tr")):
        cols = row.find_all(["td", "th"])
        text = [col.get_text(strip=True).replace("\xa0", " ") for col in cols]
        if tr_index == 0:
            headers = text
        else:
            rows.append(text)

    # Pad missing headers or values
    if len(headers) < max(len(r) for r in rows):
        headers = [""] + headers  # if missing row headers

    df = pd.DataFrame(rows, columns=headers)
    return df
def scrapCategories():
    # Setup WebDriver
    driver = webdriver.Chrome()
    driver.get("https://www.geostat.ge/")  # Replace with the actual URL

    # Wait for the main dropdown element to be present
    dropdown_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[text()='სტატისტიკური ინფორმაცია']"))
    )

    # Create an ActionChains object to hover over the main menu item
    actions = ActionChains(driver)
    actions.move_to_element(dropdown_menu).perform()

    # Wait for the sub-menu to become visible and get all the links
    dropdown_links = WebDriverWait(driver, 20).until(
        EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='header-bottom-subnav big']//ul/li/a"))
    )

    # Extract URLs from the dropdown items
    urls = [link.get_attribute('href') for link in dropdown_links]
    for url in urls:
        print(url)
    driver.quit()
    return urls


# cats = scrapCategories()
def recursiveScrap(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    time.sleep(2)

    name_tag = soup.find("h3", class_="current-page")
    name = name_tag.text.strip() if name_tag else url

    folder_data = []

    # Get table if available
    table = extract_table_from_url(url)
    if table is not None and hasattr(table, "to_dict"):
        table_data = {
            "name": name,
            "url": url,
            "type": "table",
            "data": table.to_dict(orient="records")
        }
        folder_data.append(table_data)

    # Get charts if available
    charts = extractCharts(url)
    if charts:
        chart_data = {
            "name": name,
            "url": url,
            "type": "chart",
            "data": charts
        }
        folder_data.append(chart_data)

    # Get subfolders recursively
    folders = extractFolders(url)
    for folder_url in folders:
        sub_data = recursiveScrap(folder_url)
        if sub_data:
            folder_data.extend(sub_data)

    # Return as folder structure
    return [{
        "name": name,
        "url": url,
        "type": "folder",
        "data": folder_data
    }]

def scrapData(categories=None):
    if not categories:
        categories = [
            "https://www.geostat.ge/ka/modules/categories/195/biznes-sektori",
            "https://www.geostat.ge/ka/modules/categories/92/monetaruli-statistika",
            "https://www.geostat.ge/ka/modules/categories/64/biznes-registri",
            "https://www.geostat.ge/ka/modules/categories/56/ganatleba-kultura",
            "https://www.geostat.ge/ka/modules/categories/73/garemos-statistika",
            "https://www.geostat.ge/ka/modules/categories/37/dasakmeba-khelfasebi",
            "https://www.geostat.ge/ka/modules/categories/22/erovnuli-angarishebi",
            "https://www.geostat.ge/ka/modules/categories/387/momsakhurebis-statistika298",
        ]

    all_data = []

    for url in categories:
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        time.sleep(5)
        name_tag = soup.find("h3", class_="current-page")
        category_name = name_tag.text.strip() if name_tag else url

        print(f"📁 Scraping category: {category_name}")
        result = recursiveScrap(url)
        if result:
            all_data.append({
                "name": category_name,
                "url": url,
                "type": "category",
                "data": result
            })

    # Save as MCP-style structured JSON

    with open("scraped_data_mcp1.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
        print("✅ Saved structured data to scraped_data_mcp.json")
scrapData([])