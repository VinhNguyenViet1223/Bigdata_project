# JOB 02: REVENUE BY ORDER

## Objective
Tính toán tổng doanh thu trên từng đơn hàng:
- `total_price`: Tổng tiền hàng của các mặt hàng trong đơn.
- `total_freight`: Tổng phí vận chuyển của các mặt hàng.
- `total_value`: Tổng giá trị thương mại của đơn hàng (`price + freight_value`).

## Input
- Dataset: `olist_order_items_dataset.csv`
- HDFS Input Path: `hdfs://namenode:9000/data/olist/olist_order_items_dataset.csv`

## Input Schema
```
order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value
```

## Mapper (`mapper.py`)
### Input
Dòng CSV chứa thông tin từng mặt hàng (`order_item`) từ `stdin`.
### Logic
1. Parse CSV bằng `csv.reader`.
2. Bỏ qua dòng tiêu đề (`row[0] == "order_id"`).
3. Lấy `order_id = row[0].strip()`.
4. Parse số thực: `price = float(row[5])`, `freight = float(row[6])`.
5. Loại trừ bản ghi bất thường nếu `price < 0` hoặc `freight < 0`.
6. Xuất: `order_id\tprice,freight_value`.
### Output Key
`order_id` (string 32 ký tự hexa)
### Output Value
`price,freight_value` (chuỗi số thực định dạng `"{:.2f},{:.2f}"`)

## Shuffle & Sort (Hadoop Framework)
### Grouping Key
`order_id`
### What Hadoop Does
1. Gom nhóm toàn bộ các mặt hàng của cùng một `order_id` về cùng một Reducer.
2. Sắp xếp thứ tự các bản ghi theo `order_id`.
3. Nhóm các giá trị lại:
   `order_id -> ["58.90,13.29", "25.00,10.00"]`

## Reducer (`reducer.py`)
### Input
Dòng `order_id\tprice,freight` đã được sắp xếp từ `stdin`.
### Logic
1. Tách dòng thành `order_id` và các giá trị số `price`, `freight`.
2. Cộng dồn `sum_price += price` và `sum_freight += freight`.
3. Khi hết nhóm của một `order_id`:
   - Tính `total_value = sum_price + sum_freight`.
   - Xuất: `order_id\ttotal_price\ttotal_freight\ttotal_value`.
### Output
`order_id\ttotal_price\ttotal_freight\ttotal_value`

## HDFS Output
- HDFS Output Path: `hdfs://namenode:9000/output/job02_revenue`

## Example
### Input:
```csv
00010242fe8c5a6d1ba2dd792cb16214,1,4244733e...,48436d...,2017-09-19...,58.90,13.29
00018f77f2f0320c557190d7a1444f90,1,eacb104f...,414444...,2017-05-03...,239.90,19.93
```
### Mapper Output:
```text
00010242fe8c5a6d1ba2dd792cb16214	58.90,13.29
00018f77f2f0320c557190d7a1444f90	239.90,19.93
```
### After Shuffle & Sort:
```text
00010242fe8c5a6d1ba2dd792cb16214	-> ["58.90,13.29"]
00018f77f2f0320c557190d7a1444f90	-> ["239.90,19.93"]
```
### Reducer Output:
```text
00010242fe8c5a6d1ba2dd792cb16214	58.90	13.29	72.19
00018f77f2f0320c557190d7a1444f90	239.90	19.93	259.83
```

## Execution Command
```bash
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
  -D mapreduce.framework.name=local \
  -input hdfs://namenode:9000/data/olist/olist_order_items_dataset.csv \
  -output hdfs://namenode:9000/output/job02_revenue \
  -mapper "python3 /app/src/jobs/job02_revenue/mapper.py" \
  -reducer "python3 /app/src/jobs/job02_revenue/reducer.py"
```
