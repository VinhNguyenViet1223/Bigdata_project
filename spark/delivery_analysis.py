from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    datediff,
    avg,
    countDistinct,
    sum as spark_sum,
    when,
    round as spark_round,
)


INPUT_PATH = "/tmp/olist_integrated"


spark = (
    SparkSession.builder
    .appName("T20_Olist_Delivery_Analysis")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")


print("=" * 70)
print("T20 - OLIST DELIVERY ANALYSIS")
print("=" * 70)


# ============================================================
# 1. READ INTEGRATED DATA
# ============================================================

df = spark.read.parquet(INPUT_PATH)

print(f"\nIntegrated rows: {df.count()}")


# ============================================================
# 2. PREPARE ORDER-LEVEL DELIVERY DATA
# ============================================================

delivery_df = (
    df
    .select(
        "order_id",
        "customer_state",
        "order_status",
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    )
    .dropDuplicates(["order_id"])
)


print(f"Distinct orders: {delivery_df.count()}")


# ============================================================
# 3. CALCULATE DELIVERY METRICS
# ============================================================

delivery_df = (
    delivery_df
    .withColumn(
        "delivery_days",
        datediff(
            col("order_delivered_customer_date"),
            col("order_purchase_timestamp"),
        )
    )
    .withColumn(
        "delay_days",
        datediff(
            col("order_delivered_customer_date"),
            col("order_estimated_delivery_date"),
        )
    )
    .withColumn(
        "is_late",
        when(
            col("order_delivered_customer_date")
            > col("order_estimated_delivery_date"),
            1,
        ).otherwise(0)
    )
)


# ============================================================
# 4. OVERALL DELIVERY STATISTICS
# ============================================================

completed_delivery = (
    delivery_df
    .filter(col("order_delivered_customer_date").isNotNull())
)


overall_stats = (
    completed_delivery
    .agg(
        countDistinct("order_id").alias("delivered_orders"),
        avg("delivery_days").alias("avg_delivery_days"),
        spark_sum("is_late").alias("late_orders"),
    )
    .collect()[0]
)


delivered_orders = overall_stats["delivered_orders"]
avg_delivery_days = overall_stats["avg_delivery_days"]
late_orders = overall_stats["late_orders"]


if delivered_orders > 0:
    late_rate = (late_orders / delivered_orders) * 100
else:
    late_rate = 0


print("\n" + "=" * 70)
print("1. OVERALL DELIVERY STATISTICS")
print("=" * 70)

print(f"Delivered orders      : {delivered_orders}")
print(f"Average delivery days : {avg_delivery_days:.2f}")
print(f"Late orders           : {late_orders}")
print(f"Late delivery rate    : {late_rate:.2f}%")


# ============================================================
# 5. DELIVERY PERFORMANCE BY CUSTOMER STATE
# ============================================================

delivery_by_state = (
    completed_delivery
    .filter(col("customer_state").isNotNull())
    .groupBy("customer_state")
    .agg(
        countDistinct("order_id").alias("delivered_orders"),
        avg("delivery_days").alias("avg_delivery_days"),
        spark_sum("is_late").alias("late_orders"),
    )
    .withColumn(
        "late_rate_percent",
        spark_round(
            col("late_orders")
            / col("delivered_orders")
            * 100,
            2,
        )
    )
    .orderBy(
        col("avg_delivery_days").desc()
    )
)


print("\n" + "=" * 70)
print("2. DELIVERY PERFORMANCE BY CUSTOMER STATE")
print("=" * 70)

delivery_by_state.show(30, truncate=False)


# ============================================================
# 6. TOP STATES WITH MOST LATE ORDERS
# ============================================================

late_by_state = (
    completed_delivery
    .filter(col("customer_state").isNotNull())
    .filter(col("is_late") == 1)
    .groupBy("customer_state")
    .agg(
        countDistinct("order_id").alias("late_orders")
    )
    .orderBy(
        col("late_orders").desc()
    )
)


print("\n" + "=" * 70)
print("3. TOP STATES WITH MOST LATE ORDERS")
print("=" * 70)

late_by_state.show(20, truncate=False)


# ============================================================
# 7. SAMPLE LATE ORDERS
# ============================================================

late_orders_df = (
    delivery_df
    .filter(col("is_late") == 1)
    .select(
        "order_id",
        "customer_state",
        "order_purchase_timestamp",
        "order_estimated_delivery_date",
        "order_delivered_customer_date",
        "delivery_days",
        "delay_days",
    )
    .orderBy(
        col("delay_days").desc()
    )
)


print("\n" + "=" * 70)
print("4. SAMPLE LATE ORDERS")
print("=" * 70)

late_orders_df.show(20, truncate=False)


spark.stop()