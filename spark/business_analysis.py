from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    year,
    month,
    sum as spark_sum,
    countDistinct,
)


INPUT_PATH = "/tmp/olist_integrated"


spark = (
    SparkSession.builder
    .appName("T19_Olist_Business_Analysis")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")


print("=" * 70)
print("T19 - OLIST BUSINESS ANALYSIS")
print("=" * 70)


# ============================================================
# 1. READ INTEGRATED DATA
# ============================================================

df = spark.read.parquet(INPUT_PATH)

print(f"\nIntegrated rows: {df.count()}")

print("\nSchema:")
df.printSchema()


# ============================================================
# 2. REVENUE BY MONTH
# ============================================================

revenue_by_month = (
    df
    .filter(col("order_purchase_timestamp").isNotNull())
    .filter(col("price").isNotNull())
    .withColumn("year", year(col("order_purchase_timestamp")))
    .withColumn("month", month(col("order_purchase_timestamp")))
    .groupBy("year", "month")
    .agg(
        spark_sum("price").alias("revenue")
    )
    .orderBy("year", "month")
)

print("\n" + "=" * 70)
print("1. REVENUE BY MONTH")
print("=" * 70)

revenue_by_month.show(50, truncate=False)


# ============================================================
# 3. TOP SELLERS BY REVENUE
# ============================================================

top_sellers = (
    df
    .filter(col("seller_id").isNotNull())
    .filter(col("price").isNotNull())
    .groupBy("seller_id")
    .agg(
        spark_sum("price").alias("revenue"),
        countDistinct("order_id").alias("orders")
    )
    .orderBy(col("revenue").desc())
)

print("\n" + "=" * 70)
print("2. TOP 10 SELLERS BY REVENUE")
print("=" * 70)

top_sellers.show(10, truncate=False)


# ============================================================
# 4. ORDERS BY CUSTOMER STATE
# ============================================================

orders_by_state = (
    df
    .filter(col("customer_state").isNotNull())
    .groupBy("customer_state")
    .agg(
        countDistinct("order_id").alias("orders")
    )
    .orderBy(col("orders").desc())
)

print("\n" + "=" * 70)
print("3. ORDERS BY CUSTOMER STATE")
print("=" * 70)

orders_by_state.show(30, truncate=False)


# ============================================================
# 5. TOP PRODUCTS BY REVENUE
# ============================================================

top_products = (
    df
    .filter(col("product_id").isNotNull())
    .filter(col("price").isNotNull())
    .groupBy("product_id")
    .agg(
        spark_sum("price").alias("revenue"),
        countDistinct("order_id").alias("orders")
    )
    .orderBy(col("revenue").desc())
)

print("\n" + "=" * 70)
print("4. TOP 10 PRODUCTS BY REVENUE")
print("=" * 70)

top_products.show(10, truncate=False)


spark.stop()