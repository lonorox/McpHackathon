import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from domain import DOMAIN_CONTEXT
load_dotenv()  # loads from .env

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Valid domains based on your data structure



def call_gpt4(prompt: str, model="gpt-4", temperature=0.3):

    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system",
             "content": "შენ ხარ სტატისტიკური ასისტენტი. გევალება მონაცემების მოთხოვნა რომელიც არის სტატისტიკა და ამ სტატისტიკის ანალიზი "},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


def query_handler(data, path):
    """
    Navigate through the data structure following the given path
    """
    target_category = None
    for category in data:
        if category.get("name") == path[0]:
            target_category = category
            break

    if not target_category:
        return []

    # Return the entire category data which includes all tables and charts
    return target_category


def extract_tables_and_charts(data):
    """
    Recursively walk the data to collect all tables and charts.
    """
    tables = []
    charts = []

    def walk(node):
        if isinstance(node, dict):
            node_type = node.get("type")
            if node_type == "table":
                tables.append(node.get("data", []))
            elif node_type == "chart":
                charts.append(node.get("data", []))

            # Continue traversing
            for key, value in node.items():
                if key == "data" and isinstance(value, list):
                    for item in value:
                        walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return tables, charts


def llm_full_pipeline(user_query: str, raw_data, llm=call_gpt4):
    """
    Full pipeline: map → retrieve → analyze
    """
    # Parse the raw data if it's a string
    if isinstance(raw_data, str):
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            return {
                "title": "შეცდომა მონაცემების დამუშავებისას",
                "raw_table": [],
                "analysis": "მონაცემების JSON ფორმატში გარდაქმნა ვერ მოხერხდა."
            }
    else:
        data = raw_data

    # Step 1: Identify domain
    valid_domains = list(DOMAIN_CONTEXT.keys())
    domain_prompt = f"""
    შენ ხარ სტატისტიკური ასისტენტი. განსაზღვრე, ქვემოთ მოცემული კითხვა რომელ თემატიკას ეკუთვნის.

    თემატიკის ვარიანტებია:
    {chr(10).join([f"- {d}" for d in valid_domains])}

    დაუბრუნე ჩამოთვლილი თემატიკები (ან ბევრი ან ერთი), რომლებიც ყველაზე ახლოს არის მოცემულ კითხვასთან. 
    თემატიკის სიტყვები უნდა იყოს "__" სეპარატორით გამოყოფილი (არაფერი სხვა არ დაუმატო).:
    კითხვა: "{user_query}"
    """

    domain_response = llm(domain_prompt).strip().lower().strip('"')

    response_parts = [part.strip() for part in domain_response.split("__")]
    print(response_parts)
    matched_domain = [
        domain for domain in valid_domains
        if domain.lower() in response_parts
    ]
    if not matched_domain:
        return {
            "title": "დომენი ვერ მოიძებნა",
            "raw_table": [],
            "analysis": f"შენი კითხვა ვერ დავაკავშირე შესაბამის დომენთან: {domain_response}"
        }

    # Step 2: Retrieve domain data

    all_tables, all_charts = [],[]
    for domain in matched_domain:
        path =DOMAIN_CONTEXT[domain]["path"]
        raw_result = query_handler(data, path)
        tables, charts = extract_tables_and_charts(raw_result)
        all_tables.extend(tables)
        all_charts.extend(charts)
    if not all_tables and not all_charts:
        return {
            "title": f"{matched_domain} - მონაცემები ვერ მოიძებნა",
            "raw_table": [],
            "analysis": "შესაბამისი მონაცემები ვერ მოიძებნა."
        }

    # Use first table for analysis, or combine if needed
    table = all_tables if all_tables else []
    charts = all_charts if all_charts else []

    # Step 3: Analyze
    analysis_prompt = f"""
    მომხმარებლის კითხვა:
    \"{user_query}\"

    მოცემულია შესაბამისი მონაცემები:
    {json.dumps(table, ensure_ascii=False, indent=2)}

    {"შესაბამისი დიაგრამები:" + json.dumps(charts[0], ensure_ascii=False, indent=2) if charts else ""}

    გააკეთე ანალიზი და დასკვნა, ქართულად. მოიყვანე კონკრეტული რიცხვები და ტენდენციები.
    """

    analysis = llm(analysis_prompt)

    return {
        "title": f"{matched_domain} შედეგი",
        "raw_table": table,
        "raw_charts": charts,
        "analysis": analysis.strip()
    }

