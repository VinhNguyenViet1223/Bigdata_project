import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# =========================
# 1. Cấu hình
# =========================

CSV_FILE = r"data\olist_elasticsearch.csv"
INDEX_NAME = "olist_orders"

# Kết nối Elasticsearch
es = Elasticsearch("http://localhost:9200")

# =========================
# 2. Đọc dữ liệu
# =========================

print("Đang đọc dữ liệu...")

df = pd.read_csv(CSV_FILE)

# Chuyển các giá trị NaN thành None
# để Elasticsearch có thể nhận dữ liệu rỗng
df = df.astype(object).where(pd.notna(df), None)

print("Đã đọc dữ liệu.")
print("Số dòng:", len(df))
print("Số cột:", len(df.columns))

# =========================
# 3. Tạo dữ liệu để nạp
# =========================

def generate_actions():
    for record in df.to_dict(orient="records"):
        yield {
            "_index": INDEX_NAME,
            "_source": record
        }

# =========================
# 4. Nạp dữ liệu vào Elasticsearch
# =========================

print("--------------------------------")
print("BẮT ĐẦU NẠP DỮ LIỆU")
print("--------------------------------")

success, failed = bulk(
    es,
    generate_actions(),
    chunk_size=1000,
    request_timeout=120,
    stats_only=True
)

print("--------------------------------")
print("ĐÃ NẠP DỮ LIỆU XONG")
print("--------------------------------")
print("Số document thành công:", success)
print("Số document thất bại:", failed)