import requests
import json
import pandas as pd
import sys

# Ganti dengan token dan database ID yang sesuai
NOTION_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
DATABASE_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
RELATED_DATABASE_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def safe_str(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0

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
                if title_to_find.lower().strip() in title.lower():
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
            "Akad Donasi": {
                "number": safe_float(row['Akad Donasi'])
            },
            "Nominal": {  # Kolom number di Notion
                "number": safe_float(row['Nominal'])  # Misalnya CSV punya kolom 'Amount'
            },
            "Pembayaran": {
                "select": {
                    "name": row['Pembayaran']
                }
            },
            "Tanggal Donasi": {
                "date": {
                    "start": row['Tanggal Donasi']
                }
            },
            "Waktu Transfer": {
                "rich_text": [{
                    "text": {
                        "content": safe_str(row["Waktu Transfer"])
                    }
                }]
            },
            "Nama Rekening": {
                "rich_text": [{
                    "text": {
                        "content": safe_str(row['Nama Rekening'])
                    }
                }]
            },
            "Bank yang Digunakan": {
                "rich_text": [{
                    "text": {
                        "content": safe_str(row['Bank yang Digunakan'])
                    }
                }]
            },
            "PIC": {
                "select": {
                    "name": row['PIC']
                }
            },
            "CHECK by Acc": {
                "select": {
                    "name": row['CHECK by Acc']
                }
            },
            "Jenis Program": {
                "select": {
                    "name": row['Jenis Program']
                }
            },
            "Jenis Donasi": {
                "select": {
                    "name": row['Jenis Donasi']
                }
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
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Harap masukkan path file CSV saat menjalankan skrip.")
        print("   Contoh: python3 import2.py data.csv")
    else:
        csv_file = sys.argv[1]
        import_csv_to_notion(csv_file)
