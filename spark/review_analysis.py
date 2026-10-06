from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    when,
    datediff,
    avg,
    count,
    sum as spark_sum,
    round as spark_round,
)


INPUT_PATH = "/tmp/olist_integrated"


spark = (
    SparkSession.builder
    .appName("T21_Olist_Review_Analysis")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")


print("=" * 70)
print("T21 - OLIST REVIEW ANALYSIS")
print("=" * 70)


# ============================================================
# 1. READ INTEGRATED DATA
# ============================================================

df = spark.read.parquet(INPUT_PATH)

print(f"\nIntegrated rows: {df.count()}")


# ============================================================
# 2. PREPARE ORDER-LEVEL DATA
# ============================================================

review_df = (
    df
    .select(
        "order_id",
        "customer_state",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "avg_review_score",
    )
    .dropDuplicates(["order_id"])
)

print(f"Distinct orders: {review_df.count()}")


# ============================================================
# 3. KEEP ORDERS USABLE FOR REVIEW/DELIVERY ANALYSIS
# ============================================================

review_df = (
    review_df
    .filter(col("order_delivered_customer_date").isNotNull())
    .filter(col("order_estimated_delivery_date").isNotNull())
    .filter(col("avg_review_score").isNotNull())
)


# ============================================================
# 4. CREATE DELIVERY FEATURES
# ============================================================

review_df = (
    review_df
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
    .withColumn(
        "delivery_group",
        when(
            col("is_late") == 1,
            "Late"
        ).otherwise("On-time")
    )
    .withColumn(
        "is_low_review",
        when(
            col("avg_review_score") <= 2,
            1
        ).otherwise(0)
    )
)


print(f"Orders used for analysis: {review_df.count()}")


# ============================================================
# 5. REVIEW SCORE: LATE VS ON-TIME
# ============================================================

review_by_delivery = (
    review_df
    .groupBy("delivery_group")
    .agg(
        count("*").alias("orders"),
        avg("avg_review_score").alias("avg_review_score"),
        avg("delay_days").alias("avg_delay_days"),
        spark_sum("is_low_review").alias("low_review_orders"),
    )
    .withColumn(
        "low_review_rate_percent",
        spark_round(
            col("low_review_orders")
            / col("orders")
            * 100,
            2,
        )
    )
    .withColumn(
        "avg_review_score",
        spark_round(
            col("avg_review_score"),
            2,
        )
    )
    .withColumn(
        "avg_delay_days",
        spark_round(
            col("avg_delay_days"),
            2,
        )
    )
    .orderBy("delivery_group")
)


print("\n" + "=" * 70)
print("1. REVIEW SCORE: LATE VS ON-TIME")
print("=" * 70)

review_by_delivery.show(truncate=False)


# ============================================================
# 6. REVIEW SCORE BY DELAY RANGE
# ============================================================

review_delay_group = (
    review_df
    .withColumn(
        "delay_group",
        when(
            col("delay_days") <= 0,
            "On-time"
        )
        .when(
            col("delay_days") <= 3,
            "Late 1-3 days"
        )
        .when(
            col("delay_days") <= 7,
            "Late 4-7 days"
        )
        .when(
            col("delay_days") <= 14,
            "Late 8-14 days"
        )
        .otherwise(
            "Late >14 days"
        )
    )
)


review_by_delay = (
    review_delay_group
    .groupBy("delay_group")
    .agg(
        count("*").alias("orders"),
        avg("avg_review_score").alias("avg_review_score"),
        spark_sum("is_low_review").alias("low_review_orders"),
    )
    .withColumn(
        "avg_review_score",
        spark_round(
            col("avg_review_score"),
            2,
        )
    )
    .withColumn(
        "low_review_rate_percent",
        spark_round(
            col("low_review_orders")
            / col("orders")
            * 100,
            2,
        )
    )
)


print("\n" + "=" * 70)
print("2. REVIEW SCORE BY DELAY RANGE")
print("=" * 70)

review_by_delay.show(truncate=False)


# ============================================================
# 7. REVIEW PERFORMANCE BY CUSTOMER STATE
# ============================================================

review_by_state = (
    review_df
    .filter(col("customer_state").isNotNull())
    .groupBy("customer_state")
    .agg(
        count("*").alias("orders"),
        avg("avg_review_score").alias("avg_review_score"),
        spark_sum("is_late").alias("late_orders"),
    )
    .withColumn(
        "avg_review_score",
        spark_round(
            col("avg_review_score"),
            2,
        )
    )
    .withColumn(
        "late_rate_percent",
        spark_round(
            col("late_orders")
            / col("orders")
            * 100,
            2,
        )
    )
    .orderBy(
        col("avg_review_score").asc()
    )
)


print("\n" + "=" * 70)
print("3. REVIEW PERFORMANCE BY CUSTOMER STATE")
print("=" * 70)

review_by_state.show(30, truncate=False)


# ============================================================
# 8. SAMPLE VERY LATE / LOW REVIEW ORDERS
# ============================================================

problem_orders = (
    review_df
    .filter(col("is_late") == 1)
    .filter(col("avg_review_score") <= 2)
    .select(
        "order_id",
        "customer_state",
        "order_estimated_delivery_date",
        "order_delivered_customer_date",
        "delay_days",
        "avg_review_score",
    )
    .orderBy(
        col("delay_days").desc()
    )
)


print("\n" + "=" * 70)
print("4. SAMPLE LATE ORDERS WITH LOW REVIEW")
print("=" * 70)

problem_orders.show(20, truncate=False)


spark.stop()