# JOB 01: ORDER STATISTICS

## Objective
Thống kê tổng số lượng đơn hàng theo từng trạng thái phân loại (`delivered`, `shipped`, `canceled`, `invoiced`, `processing`, `unavailable`, `created`, `approved`).

## Input
- Dataset: `olist_orders_dataset.csv`
- HDFS Input Path: `hdfs://namenode:9000/data/olist/olist_orders_dataset.csv`

## Input Schema
```
order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date
```

## Mapper (`mapper.py`)
### Input
Dòng bản ghi dạng văn bản phân cách dấu phẩy (CSV) từ `stdin`.
### Logic
1. Sử dụng module chuẩn `csv.reader` để parse đúng định dạng CSV.
2. Kiểm tra và bỏ qua dòng tiêu đề (`row[0] == "order_id"`).
3. Kiểm tra tính toàn vẹn (đủ tối thiểu 3 cột).
4. Trích xuất cột `order_status = row[2].strip().lower()`.
5. Phát sinh cặp khóa-giá trị: `order_status\t1`.
### Output Key
`order_status` (string, ví dụ: `delivered`, `shipped`, `canceled`)
### Output Value
`1` (integer)

## Shuffle & Sort (Hadoop Framework)
### Grouping Key
`order_status`
### What Hadoop Does
1. **Partitioning**: Băm khóa (hash partition) để phân phối khóa về Reducer.
2. **Sort**: Sắp xếp toàn bộ các bản ghi trung gian theo thứ tự bảng chữ cái của `order_status`.
3. **Group by Key**: Gom nhóm toàn bộ các giá trị `1` có cùng trạng thái thành một danh sách:
   `delivered -> [1, 1, 1, ...]`
   `shipped   -> [1, 1, ...]`

## Reducer (`reducer.py`)
### Input
Dòng `order_status\tcount` đã được sắp xếp từ `stdin`.
### Logic
1. Đọc tuần tự từng dòng, theo dõi biến `current_status`.
2. Khi gặp cùng một `order_status`, cộng dồn biến đếm `current_count += count`.
3. Khi chuyển sang trạng thái mới, xuất kết quả của trạng thái trước đó: `order_status\ttotal_orders`.
4. Xuất kết quả của trạng thái cuối cùng khi hết luồng.
### Output
`order_status\ttotal_orders`

## HDFS Output
- HDFS Output Path: `hdfs://namenode:9000/output/job01_order_statistics`

## Example
### Input:
```csv
e481f51cbdc54678b7cc49136f2d6af7,9ef432eb...,delivered,2017-10-02...
53cdb2fc8bc7dce0b6741e2150273451,b0830fb4...,delivered,2018-07-24...
136cce7faa42938203109c84e5787968,ed0271e0...,canceled,2018-02-19...
```
### Mapper Output:
```text
delivered	1
delivered	1
canceled	1
```
### After Shuffle & Sort:
```text
canceled	-> [1]
delivered	-> [1, 1]
```
### Reducer Output:
```text
canceled	1
delivered	2
```

## Execution Command
```bash
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
  -D mapreduce.framework.name=local \
  -input hdfs://namenode:9000/data/olist/olist_orders_dataset.csv \
  -output hdfs://namenode:9000/output/job01_order_statistics \
  -mapper "python3 /app/src/jobs/job01_order_statistics/mapper.py" \
  -reducer "python3 /app/src/jobs/job01_order_statistics/reducer.py"
```
