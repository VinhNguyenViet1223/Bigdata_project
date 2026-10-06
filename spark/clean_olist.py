from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    trim,
    to_timestamp,
    sum as spark_sum,
    when,
)
from pyspark.sql.types import StringType


INPUT_ROOT = "/tmp/olist"

FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


def clean_dataframe(df):
    # 1. Xóa các dòng trùng lặp
    df = df.dropDuplicates()

    # 2. Trim khoảng trắng ở tất cả cột kiểu string
    for field in df.schema.fields:
        if isinstance(field.dataType, StringType):
            df = df.withColumn(
                field.name,
                trim(col(field.name))
            )

    # 3. Chuẩn hóa các cột ngày giờ nếu tồn tại
    timestamp_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "shipping_limit_date",
        "review_creation_date",
        "review_answer_timestamp",
    ]

    for column_name in timestamp_columns:
        if column_name in df.columns:
            df = df.withColumn(
                column_name,
                to_timestamp(col(column_name))
            )

    return df


spark = (
    SparkSession.builder
    .appName("T17_Olist_Data_Cleaning")
    .getOrCreate()
)

print("=" * 60)
print("T17 - OLIST DATA CLEANING")
print("=" * 60)


for filename in FILES:
    path = f"{INPUT_ROOT}/{filename}"

    print("\n" + "=" * 60)
    print(f"Processing: {filename}")
    print("=" * 60)

    # Đọc CSV
    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(path)
    )

    # Số dòng trước cleaning
    before = df.count()

    # Cleaning
    cleaned = clean_dataframe(df)

    # Số dòng sau cleaning
    after = cleaned.count()

    print(f"Rows before       : {before}")
    print(f"Rows after        : {after}")
    print(f"Duplicates removed: {before - after}")

    # Thống kê null
    print("\nNull counts:")

    null_counts = cleaned.select([
        spark_sum(
            when(col(column_name).isNull(), 1).otherwise(0)
        ).alias(column_name)
        for column_name in cleaned.columns
    ])

    null_counts.show(truncate=False)

    # Kiểm tra schema sau cleaning
    print("\nSchema after cleaning:")
    cleaned.printSchema()

    # Hiển thị thử 3 dòng
    print("\nSample data:")
    cleaned.show(3, truncate=False)


spark.stop()