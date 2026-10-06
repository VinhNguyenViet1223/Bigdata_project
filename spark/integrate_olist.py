from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    sum as spark_sum,
    avg,
    count,
    max as spark_max,
)


INPUT_ROOT = "/tmp/olist"


spark = (
    SparkSession.builder
    .appName("T18_Olist_Data_Integration")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")


print("=" * 70)
print("T18 - OLIST DATA INTEGRATION")
print("=" * 70)


# ============================================================
# 1. READ DATASETS
# ============================================================

orders = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(f"{INPUT_ROOT}/olist_orders_dataset.csv")
)

customers = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(f"{INPUT_ROOT}/olist_customers_dataset.csv")
)

order_items = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(f"{INPUT_ROOT}/olist_order_items_dataset.csv")
)

payments = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(f"{INPUT_ROOT}/olist_order_payments_dataset.csv")
)

reviews = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(f"{INPUT_ROOT}/olist_order_reviews_dataset.csv")
)


print("\nInput row counts:")
print(f"orders      : {orders.count()}")
print(f"customers   : {customers.count()}")
print(f"order_items : {order_items.count()}")
print(f"payments    : {payments.count()}")
print(f"reviews     : {reviews.count()}")


# ============================================================
# 2. AGGREGATE PAYMENTS BY ORDER
# ============================================================

payments_by_order = (
    payments
    .groupBy("order_id")
    .agg(
        spark_sum("payment_value").alias("total_payment_value"),
        spark_max("payment_installments").alias("max_payment_installments"),
        count("*").alias("payment_count"),
    )
)


# ============================================================
# 3. AGGREGATE REVIEWS BY ORDER
# ============================================================

reviews_by_order = (
    reviews
    .groupBy("order_id")
    .agg(
        avg("review_score").alias("avg_review_score"),
        count("*").alias("review_count"),
    )
)


# ============================================================
# 4. ORDERS + CUSTOMERS
# ============================================================

orders_customers = (
    orders.alias("o")
    .join(
        customers.alias("c"),
        col("o.customer_id") == col("c.customer_id"),
        "left",
    )
    .select(
        col("o.order_id"),
        col("o.customer_id"),
        col("c.customer_unique_id"),
        col("c.customer_city"),
        col("c.customer_state"),
        col("o.order_status"),
        col("o.order_purchase_timestamp"),
        col("o.order_approved_at"),
        col("o.order_delivered_carrier_date"),
        col("o.order_delivered_customer_date"),
        col("o.order_estimated_delivery_date"),
    )
)


# ============================================================
# 5. ADD ORDER ITEMS
# ============================================================

integrated_df = (
    orders_customers.alias("oc")
    .join(
        order_items.alias("oi"),
        col("oc.order_id") == col("oi.order_id"),
        "left",
    )
    .select(
        col("oc.*"),
        col("oi.order_item_id"),
        col("oi.product_id"),
        col("oi.seller_id"),
        col("oi.shipping_limit_date"),
        col("oi.price"),
        col("oi.freight_value"),
    )
)


# ============================================================
# 6. ADD PAYMENT INFORMATION
# ============================================================

integrated_df = (
    integrated_df.alias("base")
    .join(
        payments_by_order.alias("p"),
        col("base.order_id") == col("p.order_id"),
        "left",
    )
    .select(
        col("base.*"),
        col("p.total_payment_value"),
        col("p.max_payment_installments"),
        col("p.payment_count"),
    )
)


# ============================================================
# 7. ADD REVIEW INFORMATION
# ============================================================

integrated_df = (
    integrated_df.alias("base")
    .join(
        reviews_by_order.alias("r"),
        col("base.order_id") == col("r.order_id"),
        "left",
    )
    .select(
        col("base.*"),
        col("r.avg_review_score"),
        col("r.review_count"),
    )
)


# ============================================================
# 8. VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("INTEGRATION RESULT")
print("=" * 70)

integrated_count = integrated_df.count()

print(f"Integrated rows: {integrated_count}")

print("\nSchema:")
integrated_df.printSchema()

print("\nSample data:")
integrated_df.show(10, truncate=False)


# ============================================================
# 9. BASIC QUALITY CHECK
# ============================================================

distinct_orders = (
    integrated_df
    .select("order_id")
    .distinct()
    .count()
)

missing_customer = (
    integrated_df
    .filter(col("customer_unique_id").isNull())
    .count()
)

missing_payment = (
    integrated_df
    .filter(col("total_payment_value").isNull())
    .count()
)

missing_review = (
    integrated_df
    .filter(col("avg_review_score").isNull())
    .count()
)


print("\n" + "=" * 70)
print("QUALITY CHECK")
print("=" * 70)

print(f"Distinct orders              : {distinct_orders}")
print(f"Missing customer information : {missing_customer}")
print(f"Missing payment information  : {missing_payment}")
print(f"Missing review information   : {missing_review}")


spark.stop()