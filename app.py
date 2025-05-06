
from llm.llm import llm_full_pipeline, call_gpt4
import json
def handle_user_query(query, llm, data):
    return llm_full_pipeline(query, data, llm)
def load_data():
    with open("../hackathoMCP/data/scraped_data_mcp1.json", "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    print("🇬🇪 სტატისტიკური ასისტენტი მზადაა.\n")
    data = load_data()

    while True:
        try:
            query = input("❓ კითხვა: ").strip()
            if query.lower() in {"exit", "quit", "გასვლა"}:
                print("👋 ნახვამდის!")
                break

            result = handle_user_query(query, call_gpt4, data)
            print(f"\n📌 {result['title']}")
            print(f"\n📊 მონაცემები ({len(result['raw_table'])} ჩანაწერი):")
            # print(json.dumps(result["raw_table"], indent=2, ensure_ascii=False))

            print(f"\n🧠 ანალიზი:\n{result['analysis']}\n")

        except KeyboardInterrupt:
            print("\n👋 დასრულდა.")
            break
        except Exception as e:
            print(f"❌ შეცდომა: {e}\n")

if __name__ == "__main__":
    main()


