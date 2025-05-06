from domain import DOMAIN_CONTEXT

def query_handler(query, data):
    matches = []

    def search(name, content):
        # Match on category or subcategory name
        if query.lower() in name.lower():
            matches.append({name: content})

        # Search inside nested folders
        folders = content.get("folders", [])
        for folder in folders:
            for sub_name, sub_content in folder.items():
                search(sub_name, sub_content)

        # Optional: You can also search inside chart titles or table headers
        if content.get("charts"):
            for chart in content["charts"]:
                if "title" in chart and query.lower() in chart["title"].lower():
                    matches.append({"chart_match": chart})

        if content.get("table"):
            for row in content["table"]:
                if any(query.lower() in str(val).lower() for val in row.values()):
                    matches.append({"table_row_match": row})

    for category in data:
        name = category.get("name")
        content = category.get("data", {})
        search(name, content)

    return matches or [{"message": "❌ ვერ მოიძებნა შესაბამისი ინფორმაცია"}]