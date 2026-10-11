# JOB 03: CATEGORY ANALYSIS (MULTI-TABLE JOIN)

## Objective
Thực hiện liên kết (JOIN) 3 bảng dữ liệu để phân tích hoạt động thương mại theo từng danh mục sản phẩm dịch sang tiếng Anh (`category`):
- `total_items`: Số lượng sản phẩm bán được.
- `total_price`: Tổng doanh thu từ tiền hàng.
- `total_freight`: Tổng phí vận chuyển hàng hóa.
- `total_value`: Tổng giá trị thương mại phát sinh (`price + freight_value`).

## Input Datasets
1. Fact Table: `olist_order_items_dataset.csv` (112,650 dòng, ~15MB)
2. Dimension Table 1: `olist_products_dataset.csv` (32,951 dòng, ~2.3MB)
3. Dimension Table 2: `product_category_name_translation.csv` (71 dòng, ~2.6KB)
- HDFS Input Path: `hdfs://namenode:9000/data/olist/olist_order_items_dataset.csv`

## Join Strategy: Map-Side Join / Distributed Cache Lookup
- **Lý do thiết kế:**
  Trong mô hình Star Schema, bảng Fact (`order_items`) chứa hơn 112k dòng giao dịch trong khi các bảng danh mục Dimension (`products` 2.3MB và `translation` 2.6KB) có dung lượng rất nhỏ so với bộ nhớ RAM của một worker container (vài GB RAM).
  Nếu sử dụng Reduce-Side Join, toàn bộ 112k bản ghi items cùng 33k bản ghi products sẽ bị phát sinh ra đĩa, đẩy qua mạng mạng trong pha Shuffle I/O gây nghẽn cổ chai mạng (network bottleneck).
  Bằng cách áp dụng **Map-Side Join**, Mapper nạp 2 bảng tra cứu vào bộ nhớ (In-memory Hash Map). Khi đọc luồng streaming lớn từ `stdin`, Mapper thực hiện tra cứu $O(1)$ để chuyển đổi `product_id -> product_category_name -> english_category`.
- **Xử lý ngoại lệ dữ liệu:**
  - Ký tự ẩn UTF-8 BOM (`\ufeff`) ở đầu file translation được tự động strip.
  - Các sản phẩm có category chưa có bản dịch (như `pc_gamer`) được giữ lại tên gốc.
  - Các sản phẩm khuyết category (610 sản phẩm null) được gom vào nhóm `"unknown"`.

## Mapper (`mapper.py`)
### Input
Dòng CSV từ `olist_order_items_dataset.csv` qua `stdin`.
### Logic
1. Khởi tạo và nạp `translation_map` và `product_map` vào bộ nhớ.
2. Đọc từng dòng item, lấy `product_id`, `price`, `freight`.
3. Tra cứu danh mục: `category = product_map.get(product_id, "unknown")`.
4. Tính `item_value = price + freight`.
5. Xuất: `category\t1,price,freight,item_value`.
### Output Key
`category` (ví dụ: `bed_bath_table`, `health_beauty`, `computers_accessories`)
### Output Value
`1,price,freight,item_value`

## Shuffle & Sort (Hadoop Framework)
### Grouping Key
`category`
### What Hadoop Does
1. Gom toàn bộ các bản ghi có cùng `category` về cùng một Reducer.
2. Sắp xếp thứ tự bảng chữ cái theo tên `category`.
3. Tạo nhóm: `category -> ["1,58.90,13.29,72.19", "1,25.00,10.00,35.00", ...]`

## Reducer (`reducer.py`)
### Input
Dòng `category\t1,price,freight,value` đã được sắp xếp từ `stdin`.
### Logic
1. Duyệt tuần tự qua các bản ghi của từng `category`.
2. Cộng dồn: `total_items += 1`, `total_price += price`, `total_freight += freight`, `total_value += value`.
3. Khi hết nhóm, xuất: `category\ttotal_items\ttotal_price\ttotal_freight\ttotal_value`.
### Output Schema
`category\ttotal_items\ttotal_price\ttotal_freight\ttotal_value`

## HDFS Output
- HDFS Output Path: `hdfs://namenode:9000/output/job03_category`

## Execution Command
```bash
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
  -D mapreduce.framework.name=local \
  -files /app/data/olist_products_dataset.csv,/app/data/product_category_name_translation.csv \
  -input hdfs://namenode:9000/data/olist/olist_order_items_dataset.csv \
  -output hdfs://namenode:9000/output/job03_category \
  -mapper "python3 /app/src/jobs/job03_category/mapper.py" \
  -reducer "python3 /app/src/jobs/job03_category/reducer.py"
```
