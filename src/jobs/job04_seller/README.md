# JOB 04: SELLER PERFORMANCE

## Objective
Phân tích hiệu suất kinh doanh của từng người bán (`seller_id`):
- `total_items`: Tổng số mặt hàng người bán đã bán thành công.
- `total_price`: Tổng doanh thu tiền hàng tạo ra.
- `total_freight`: Tổng chi phí vận chuyển.
- `total_value`: Tổng giá trị thương mại của người bán (`total_price + total_freight`).

## Input
- Dataset: `olist_order_items_dataset.csv`
- HDFS Input Path: `hdfs://namenode:9000/data/olist/olist_order_items_dataset.csv`

## Input Schema
```
order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value
```

## Mapper (`mapper.py`)
### Input
Dòng bản ghi mặt hàng từ `stdin`.
### Logic
1. Parse CSV bằng `csv.reader`.
2. Bỏ qua header (`row[0] == "order_id"`).
3. Lấy `seller_id = row[3].strip()`.
4. Parse số thực `price` và `freight`, tính `value = price + freight`.
5. Loại trừ các bản ghi có giá trị âm bất thường.
6. Xuất: `seller_id\t1,price,freight,value`.
### Output Key
`seller_id` (string 32 ký tự)
### Output Value
`1,price,freight,value`

## Shuffle & Sort (Hadoop Framework)
### Grouping Key
`seller_id`
### What Hadoop Does
1. Phân vùng băm (Hash Partition) theo `seller_id`.
2. Sắp xếp toàn bộ bản ghi tăng dần theo `seller_id`.
3. Gom nhóm toàn bộ giao dịch của cùng một người bán:
   `seller_id -> ["1,58.90,13.29,72.19", "1,239.90,19.93,259.83", ...]`

## Reducer (`reducer.py`)
### Input
Dòng `seller_id\t1,price,freight,value` đã được sắp xếp từ `stdin`.
### Logic
1. Lặp qua các bản ghi của từng `seller_id`.
2. Cộng dồn `total_items`, `total_price`, `total_freight`, `total_value`.
3. Khi hết nhóm của một người bán, xuất: `seller_id\ttotal_items\ttotal_price\ttotal_freight\ttotal_value`.
### Output Schema
`seller_id\ttotal_items\ttotal_price\ttotal_freight\ttotal_value`

## HDFS Output
- HDFS Output Path: `hdfs://namenode:9000/output/job04_seller`

## Execution Command
```bash
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
  -D mapreduce.framework.name=local \
  -input hdfs://namenode:9000/data/olist/olist_order_items_dataset.csv \
  -output hdfs://namenode:9000/output/job04_seller \
  -mapper "python3 /app/src/jobs/job04_seller/mapper.py" \
  -reducer "python3 /app/src/jobs/job04_seller/reducer.py"
```
