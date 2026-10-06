import pandas as pd
import os

# =========================
# 1. Đường dẫn dữ liệu
# =========================

DATA_DIR = "data"

# =========================
# 2. Đọc các bảng Olist
# =========================

orders = pd.read_csv(
    os.path.join(DATA_DIR, "olist_orders_dataset.csv")
)

order_items = pd.read_csv(
    os.path.join(DATA_DIR, "olist_order_items_dataset.csv")
)

products = pd.read_csv(
    os.path.join(DATA_DIR, "olist_products_dataset.csv")
)

customers = pd.read_csv(
    os.path.join(DATA_DIR, "olist_customers_dataset.csv")
)

sellers = pd.read_csv(
    os.path.join(DATA_DIR, "olist_sellers_dataset.csv")
)

reviews = pd.read_csv(
    os.path.join(DATA_DIR, "olist_order_reviews_dataset.csv")
)

category_translation = pd.read_csv(
    os.path.join(DATA_DIR, "product_category_name_translation.csv")
)

print("Đã đọc dữ liệu.")

# =========================
# 3. Xử lý bảng Reviews
# =========================
# Một đơn hàng có thể có nhiều review.
# Ta lấy điểm đánh giá trung bình theo order_id.

reviews_agg = reviews.groupby("order_id").agg(
    review_score=("review_score", "mean"),
    review_comment_title=("review_comment_title", "first"),
    review_comment_message=("review_comment_message", "first")
).reset_index()

# =========================
# 4. Ghép Order Items + Orders
# =========================

df = order_items.merge(
    orders,
    on="order_id",
    how="left"
)

# =========================
# 5. Ghép thông tin khách hàng
# =========================

df = df.merge(
    customers,
    on="customer_id",
    how="left"
)

# =========================
# 6. Ghép thông tin sản phẩm
# =========================

df = df.merge(
    products,
    on="product_id",
    how="left"
)

# =========================
# 7. Ghép thông tin người bán
# =========================

df = df.merge(
    sellers,
    on="seller_id",
    how="left"
)

# =========================
# 8. Ghép đánh giá
# =========================

df = df.merge(
    reviews_agg,
    on="order_id",
    how="left"
)

# =========================
# 9. Ghép tên danh mục tiếng Anh
# =========================

df = df.merge(
    category_translation,
    on="product_category_name",
    how="left"
)

# =========================
# 10. Tính thời gian giao hàng
# =========================

df["order_delivered_customer_date"] = pd.to_datetime(
    df["order_delivered_customer_date"],
    errors="coerce"
)

df["order_purchase_timestamp"] = pd.to_datetime(
    df["order_purchase_timestamp"],
    errors="coerce"
)

df["order_estimated_delivery_date"] = pd.to_datetime(
    df["order_estimated_delivery_date"],
    errors="coerce"
)

# Số ngày từ lúc đặt hàng đến lúc khách nhận hàng
df["delivery_days"] = (
    df["order_delivered_customer_date"]
    - df["order_purchase_timestamp"]
).dt.total_seconds() / 86400

df["delivery_days"] = df["delivery_days"].round(2)

# =========================
# 11. Xác định giao hàng trễ
# =========================

df["is_late"] = (
    df["order_delivered_customer_date"]
    > df["order_estimated_delivery_date"]
)

df["is_late"] = df["is_late"].fillna(False)

# =========================
# 12. Tạo doanh thu của từng sản phẩm
# =========================

df["item_revenue"] = (
    df["price"] + df["freight_value"]
)

# =========================
# 13. Đổi tên một số cột
# =========================

df = df.rename(columns={
    "customer_city": "customer_city",
    "customer_state": "customer_state",
    "seller_city": "seller_city",
    "seller_state": "seller_state",
    "product_category_name_english": "category_english"
})

# =========================
# 14. Chọn các cột cần thiết
# =========================

columns = [
    "order_id",
    "order_item_id",
    "product_id",
    "product_category_name",
    "category_english",
    "seller_id",
    "customer_id",

    "order_status",
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",

    "customer_city",
    "customer_state",

    "seller_city",
    "seller_state",

    "price",
    "freight_value",
    "item_revenue",

    "delivery_days",
    "is_late",

    "review_score",
    "review_comment_title",
    "review_comment_message"
]

df = df[columns]

# =========================
# 15. Xuất dữ liệu
# =========================

output_file = os.path.join(
    DATA_DIR,
    "olist_elasticsearch.csv"
)

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

# =========================
# 16. Thống kê kết quả
# =========================

print("--------------------------------")
print("ĐÃ GHÉP DỮ LIỆU THÀNH CÔNG")
print("--------------------------------")

print("Số document:", len(df))
print("Số cột:", len(df.columns))

print("\n5 dòng đầu tiên:")
print(df.head())

print("\nFile kết quả:")
print(output_file)