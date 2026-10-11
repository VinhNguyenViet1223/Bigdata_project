# JOB 06: DELIVERY LOGISTICS ANALYSIS

## Objective
Phân tích hiệu suất vận hành chuỗi cung ứng và giao nhận hàng hóa của Olist:
- Tính thời gian vận chuyển thực tế: `delivery_days = delivered_customer_date - purchase_timestamp`.
- Xác định đơn hàng giao trễ hạn: `delivered_customer_date > order_estimated_delivery_date`.
- Tính các chỉ số logistics trọng yếu:
  - `total_delivered_orders`: Tổng số đơn giao hàng thành công có đủ ngày tháng.
  - `avg_delivery_days`: Thời gian giao hàng trung bình (ngày).
  - `min_delivery_days`: Thời gian giao hàng nhanh nhất.
  - `max_delivery_days`: Thời gian giao hàng lâu nhất.
  - `late_orders`: Số lượng đơn hàng bị giao trễ so với dự kiến.
  - `on_time_orders`: Số lượng đơn hàng giao đúng hạn hoặc sớm hơn dự kiến.
  - `late_delivery_rate_pct`: Tỷ lệ phần trăm đơn hàng giao trễ hạn (%).

## Input
- Dataset: `olist_orders_dataset.csv`
- HDFS Input Path: `hdfs://namenode:9000/data/olist/olist_orders_dataset.csv`

## Input Schema
```
order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date
```

## Mapper (`mapper.py`)
### Input
Dòng bản ghi đơn hàng từ `stdin`.
### Logic
1. Parse CSV bằng `csv.reader`.
2. Bỏ qua header (`row[0] == "order_id"`).
3. Chỉ xử lý các đơn hàng có `order_status == "delivered"`.
4. Bỏ qua các đơn khuyết thiếu ngày tháng (2,965 đơn chưa hoàn tất hoặc thiếu timestamp).
5. Parse `purchase_timestamp`, `delivered_customer_date`, `estimated_delivery_date`.
6. Tính `delivery_days = (delivered - purchase).total_seconds() / 86400.0`.
7. Đánh dấu cờ trễ: `is_late = 1` nếu `delivered > estimated`, ngược lại `0`.
8. Xuất: `DELIVERY_METRICS\tdelivery_days,is_late`.
### Output Key
`DELIVERY_METRICS`
### Output Value
`delivery_days,is_late`

## Shuffle & Sort (Hadoop Framework)
### Grouping Key
`DELIVERY_METRICS`
### What Hadoop Does
Gom toàn bộ các cặp số liệu thời gian giao hàng về cùng một Reducer dưới khóa `DELIVERY_METRICS`.

## Reducer (`reducer.py`)
### Input
Dòng `DELIVERY_METRICS\tdelivery_days,is_late` từ `stdin`.
### Logic
1. Lặp qua tất cả bản ghi, tính `total_count`, `sum_days`, cập nhật `min_days`, `max_days`, và đếm `late_count`.
2. Tính `avg_days = sum_days / total_count`.
3. Tính `late_rate = (late_count / total_count) * 100.0`.
4. Xuất bảng thống kê chỉ số logistics.
### Output Schema
```
total_delivered_orders    <count>
avg_delivery_days         <avg_days>
min_delivery_days         <min_days>
max_delivery_days         <max_days>
late_orders               <late_count>
on_time_orders            <on_time_count>
late_delivery_rate_pct    <rate>%
```

## HDFS Output
- HDFS Output Path: `hdfs://namenode:9000/output/job06_delivery`

## Execution Command
```bash
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
  -D mapreduce.framework.name=local \
  -input hdfs://namenode:9000/data/olist/olist_orders_dataset.csv \
  -output hdfs://namenode:9000/output/job06_delivery \
  -mapper "python3 /app/src/jobs/job06_delivery/mapper.py" \
  -reducer "python3 /app/src/jobs/job06_delivery/reducer.py"
```
