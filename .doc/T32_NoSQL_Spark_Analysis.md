

# T32 - Báo cáo NoSQL, Spark và Data Analysis

## 1. Tổng quan

Phần này trình bày các công việc liên quan đến MongoDB, Apache Spark và phân tích dữ liệu trong dự án Olist.

Luồng xử lý chính:

Olist CSV  
→ MongoDB  
→ Spark Data Cleaning  
→ Spark Data Integration  
→ Business Analysis  
→ Delivery Analysis  
→ Review Analysis

Các task chính được thực hiện gồm:

- T12: Thiết kế MongoDB Document
- T13: Triển khai MongoDB bằng Docker
- T14: Import dữ liệu Olist vào MongoDB
- T15: MongoDB Aggregation
- T16: Spark Master/Worker bằng Docker
- T17: Data Cleaning bằng PySpark
- T18: Data Integration bằng PySpark
- T19: Business Analysis
- T20: Delivery Analysis
- T21: Review Analysis

# 2. MongoDB / NoSQL

## 2.1. Thiết kế dữ liệu MongoDB - T12

Dữ liệu Olist gồm nhiều tập dữ liệu liên quan đến khách hàng, đơn hàng, sản phẩm, người bán, thanh toán và đánh giá.

Các collection chính được sử dụng:

- customers
- geolocation
- orders
- order_items
- order_payments
- order_reviews
- products
- sellers
- category_translation

Thiết kế MongoDB được xây dựng nhằm:

- lưu trữ dữ liệu Olist dưới dạng document;
- hỗ trợ truy vấn dữ liệu linh hoạt;
- làm cơ sở cho các truy vấn aggregation;
- phục vụ phân tích dữ liệu NoSQL.

## 2.2. Triển khai MongoDB bằng Docker - T13

MongoDB được triển khai bằng Docker.

Thông tin chính:

- Container: `olist-mongodb`
- Image: `mongo:7`
- Port: `27017`

Quá trình kiểm thử gồm:

- tạo database `olist`;
- tạo collection kiểm thử;
- thực hiện `insertOne()`;
- thực hiện `find()`;
- restart container và kiểm tra dữ liệu vẫn tồn tại.

Kết quả cho thấy MongoDB hoạt động ổn định và volume lưu trữ dữ liệu đúng.

## 2.3. Import dữ liệu Olist - T14

Toàn bộ 9 file CSV của Olist được import vào MongoDB.

Số lượng document chính:

| Collection | Documents |
|---|---:|
| customers | 99,441 |
| geolocation | 1,000,163 |
| order_items | 112,650 |
| order_payments | 103,886 |
| order_reviews | 99,224 |
| orders | 99,441 |
| products | 32,951 |
| sellers | 3,095 |
| category_translation | 71 |

Dữ liệu được import bằng `mongoimport`.

Các tùy chọn chính:

- `--headerline`
- `--drop`

Việc sử dụng `--drop` giúp tránh dữ liệu bị import trùng trong các lần chạy lại.

## 2.4. MongoDB Aggregation - T15

Các truy vấn aggregation được thực hiện tương đương với các thao tác:

- GROUP BY
- SUM
- COUNT
- JOIN bằng `$lookup`

Một số kết quả chính:

- Tổng `payment_value`: 16,008,872.12
- `credit_card` là phương thức thanh toán có doanh thu cao
- Số đơn hàng trạng thái `delivered`: 96,478
- Xác định Top Seller theo doanh thu
- Xác định Top Category bằng `$lookup` giữa `order_items` và `products`

Một kết quả nổi bật:

`beleza_saude`

- total_sales: 1,258,681.34
- items_sold: 9,670

# 3. Apache Spark

## 3.1. Spark Cluster - T16

Apache Spark được triển khai bằng Docker theo mô hình standalone cluster.

Cấu trúc:

Spark Master  
→ Spark Worker

Thông tin:

- Spark version: 3.5.1
- Master port: 7077
- Master UI: 8080
- Worker UI: 8081
- Worker trạng thái: ALIVE

Spark Worker kết nối tới:

`spark://spark-master:7077`

Cluster này được sử dụng cho các task T17–T21.

## 3.2. Data Cleaning - T17

T17 sử dụng PySpark để làm sạch 9 file CSV.

Luồng xử lý:

CSV  
→ Spark read  
→ inferSchema  
→ dropDuplicates  
→ trim string  
→ parse timestamp  
→ thống kê null  
→ kiểm tra schema  
→ DataFrame cleaned

Các bước cleaning chính:

- loại bỏ duplicate;
- trim khoảng trắng ở các cột string;
- chuyển các trường thời gian sang kiểu timestamp;
- kiểm tra số lượng null;
- kiểm tra schema sau khi xử lý.

Job được kiểm thử ở:

- local mode;
- Spark standalone cluster.

Job kết thúc thành công với `exitCode 0`.

# 4. Data Integration - T18

## 4.1. Các nguồn dữ liệu

T18 tích hợp các bảng:

- orders
- customers
- order_items
- order_payments
- order_reviews

Luồng join:

orders  
→ customers bằng `customer_id`  
→ order_items bằng `order_id`  
→ payments bằng `order_id`  
→ reviews bằng `order_id`

Payments và reviews được aggregate trước khi join để tránh hiện tượng nhân bản dữ liệu do quan hệ nhiều-nhiều.

## 4.2. Kết quả Integration

Input:

- orders: 99,441
- customers: 99,441
- order_items: 112,650
- payments: 103,886
- reviews: 104,162

Kết quả:

- Integrated rows: 113,425
- Distinct orders: 99,441
- Missing customer information: 0
- Missing payment information: 3
- Missing review information: 961

Kết quả cho thấy toàn bộ 99,441 `order_id` vẫn được giữ lại sau quá trình integration.

## 4.3. Output Parquet

Integrated DataFrame được ghi thành Parquet:

`/tmp/olist_integrated`

Output gồm nhiều file:

`part-xxxxx.snappy.parquet`

và file:

`_SUCCESS`

Dung lượng output khoảng 20 MB.

Parquet này được sử dụng làm input cho các task T19–T21.

# 5. Business Analysis - T19

T19 sử dụng dữ liệu tích hợp để phân tích các chỉ số kinh doanh.

Các phân tích gồm:

## 5.1. Revenue by Month

Doanh thu được tổng hợp theo:

- year
- month

Nguồn tính doanh thu:

`price`

Phân tích này cho phép theo dõi biến động doanh thu theo thời gian.

## 5.2. Top Sellers by Revenue

Dữ liệu được group theo:

`seller_id`

Các metric:

- revenue
- số order

Sau đó sắp xếp giảm dần theo revenue để tìm seller có doanh thu cao nhất.

## 5.3. Orders by Customer State

Số đơn hàng được tổng hợp theo:

`customer_state`

Metric sử dụng:

`countDistinct(order_id)`

Phân tích này xác định khu vực có nhiều đơn hàng nhất.

## 5.4. Top Products by Revenue

Dữ liệu được group theo:

`product_id`

Các metric:

- revenue
- số order

Kết quả được sắp xếp giảm dần theo revenue.

# 6. Delivery Analysis - T20

## 6.1. Chuẩn bị dữ liệu

Do integrated DataFrame có thể chứa nhiều dòng cho cùng một order do `order_items`, T20 chuyển dữ liệu về grain:

`1 dòng / 1 order`

bằng:

`dropDuplicates(["order_id"])`

## 6.2. Các metric Delivery

### Delivery Days

`delivery_days = order_delivered_customer_date - order_purchase_timestamp`

### Delay Days

`delay_days = order_delivered_customer_date - order_estimated_delivery_date`

### Late Order

Order được coi là giao trễ khi:

`order_delivered_customer_date > order_estimated_delivery_date`

## 6.3. Kết quả tổng thể

Kết quả:

- Delivered orders: 96,476
- Average delivery days: 12.50 ngày
- Late orders: 7,827
- Late delivery rate: 8.11%

Như vậy phần lớn đơn hàng được giao đúng hoặc trước thời gian dự kiến.

## 6.4. Delivery theo khu vực

Một số kết quả:

- SP có số đơn giao lớn nhất
- SP có 2,387 đơn giao trễ
- RJ có 1,664 đơn giao trễ
- MG có 638 đơn giao trễ

Một số bang có thời gian giao hàng trung bình cao:

- RR: khoảng 29.34 ngày
- AP: khoảng 27.18 ngày
- AM: khoảng 26.36 ngày
- AL: khoảng 24.50 ngày

Kết quả cho thấy hiệu suất giao hàng khác nhau đáng kể giữa các khu vực.

# 7. Review Analysis - T21

## 7.1. Mục tiêu

T21 tập trung trả lời câu hỏi:

"Giao hàng trễ có ảnh hưởng tới điểm đánh giá khách hàng hay không?"

Dữ liệu được đưa về:

`1 order / 1 dòng`

và chỉ giữ các order có:

- thời gian giao thực tế;
- thời gian giao dự kiến;
- review score.

## 7.2. Late vs On-time

Kết quả:

| Delivery Group | Orders | Avg Review Score | Avg Delay Days | Low Review Rate |
|---|---:|---:|---:|---:|
| Late | 7,662 | 2.57 | 8.76 | 53.98% |
| On-time | 88,168 | 4.29 | -13.71 | 9.19% |

Kết quả cho thấy:

- đơn giao đúng hạn có review trung bình khoảng 4.29;
- đơn giao trễ chỉ có review trung bình khoảng 2.57;
- tỷ lệ review thấp của nhóm giao trễ là 53.98%;
- tỷ lệ review thấp của nhóm đúng hạn chỉ khoảng 9.19%.

Dữ liệu cho thấy giao hàng trễ có mối liên hệ rõ rệt với mức đánh giá thấp hơn.

## 7.3. Review theo mức độ giao trễ

| Delay Group | Orders | Avg Review Score | Low Review Rate |
|---|---:|---:|---:|
| On-time | 89,448 | 4.29 | 9.24% |
| Late 1–3 days | 1,852 | 3.29 | 32.18% |
| Late 4–7 days | 1,748 | 2.11 | 67.56% |
| Late 8–14 days | 1,447 | 1.67 | 80.03% |
| Late >14 days | 1,335 | 1.73 | 78.20% |

Xu hướng tổng thể:

thời gian giao trễ tăng  
→ điểm review trung bình giảm  
→ tỷ lệ review thấp tăng.

Điều này tiếp tục củng cố nhận định rằng trải nghiệm giao hàng có liên hệ mạnh với mức độ hài lòng của khách hàng.

# 8. Kết luận

Phần MongoDB và Spark đã xây dựng được pipeline xử lý dữ liệu Olist gồm:

CSV  
→ MongoDB  
→ Spark Cleaning  
→ Spark Integration  
→ Parquet  
→ Business Analysis  
→ Delivery Analysis  
→ Review Analysis

Các kết quả chính:

- MongoDB lưu trữ thành công dữ liệu Olist;
- Spark standalone cluster hoạt động ổn định;
- 99,441 đơn hàng được giữ đầy đủ sau integration;
- thời gian giao hàng trung bình khoảng 12.50 ngày;
- tỷ lệ giao trễ khoảng 8.11%;
- đơn giao đúng hạn có review trung bình 4.29;
- đơn giao trễ có review trung bình 2.57;
- nhóm giao trễ có tỷ lệ review thấp 53.98%, cao hơn nhiều so với 9.19% ở nhóm đúng hạn.

Kết quả phân tích cho thấy hiệu suất giao hàng là một yếu tố có mối liên hệ mạnh với mức độ hài lòng và đánh giá của khách hàng.

Lưu ý: kết quả trên thể hiện mối liên hệ trong dữ liệu quan sát, không khẳng định quan hệ nhân quả.