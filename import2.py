import requests
import json
import pandas as pd

# Ganti dengan token dan database ID yang sesuai
NOTION_TOKEN = "xxxxxxxxxxxxxxx"
DATABASE_ID = "xxxxxxxxxxxxxxxxxx"
RELATED_DATABASE_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_page_id_by_title(title_to_find):
    url = f"https://api.notion.com/v1/databases/{RELATED_DATABASE_ID}/query"
    has_more = True
    next_cursor = None

    while has_more:
        # payload = {"page_size": 100}
        payload = {
        "filter": {
            "property": "Nama Lengkap",  # sesuaikan dengan nama kolom title kamu
            "rich_text": {
                "equals": title_to_find
                }
            }
        }
        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        results = data.get("results", [])

        for result in results:
            title_property = result["properties"].get("Nama Lengkap", {}).get("title", [])
            if title_property:
                title = title_property[0]["text"]["content"]
                if title == title_to_find:
                    return result["id"]

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    return None

# def get_page_id_by_title(title_to_find):
#     url = f"https://api.notion.com/v1/databases/{RELATED_DATABASE_ID}/query"
#     response = requests.post(url, headers=headers)
#     results = response.json().get("results", [])
#     # print(json.dumps(results, indent=1));
#     for result in results:
#         title_property = result["properties"].get("Nama Lengkap", {}).get("title", [])
#         if title_property:
#             title = title_property[0]["text"]["content"]
#             # printt(title);
#             # print(title_to_find);
#             if title == title_to_find:
#                 return result["id"]
#     return None

def convert_row_to_notion_format(row):
    print(get_page_id_by_title(row['Nama']));
    related_id = get_page_id_by_title(row['Nama'])  # RelatedName dari CSV

    return {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Keterangan": {  # Kolom Title di Notion
                "title": [
                    {
                        "text": {
                            "content": str(row['Keterangan'])  # Ambil dari kolom 'Name' di CSV
                        }
                    }
                ]
            },
            "Nama": {  # Kolom relation di Notion
                "relation": [
                    {
                        "id": related_id  # Ambil dari fungsi pencocokan nama
                    }
                ] if related_id else []
            },
            "Nominal": {  # Kolom number di Notion
                "number": float(row['Nominal'])  # Misalnya CSV punya kolom 'Amount'
            }
        }
    }

def import_csv_to_notion(csv_file_path):
    df = pd.read_csv(csv_file_path)
    print(f"Total baris yang akan diimpor: {len(df)}")

    for index, row in df.iterrows():
        data = convert_row_to_notion_format(row)
        response = requests.post("https://api.notion.com/v1/pages", headers=headers, data=json.dumps(data))

        if response.status_code in [200, 201]:
            print(f"✔️ Baris {index+1} berhasil diunggah.")
        else:
            print(f"❌ Gagal mengunggah baris {index+1}. Response: {response.text}")

# Contoh penggunaan:
import_csv_to_notion("template.csv")
