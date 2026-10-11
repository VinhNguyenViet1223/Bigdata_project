# JOB 05: CUSTOMER REVIEWS ANALYSIS

## Objective
Phân tích trải nghiệm và mức độ hài lòng của khách hàng trên toàn sàn:
- Phân phối số lượng đánh giá theo từng mức điểm từ 1 đến 5 sao (`SCORE_1` đến `SCORE_5`).
- Điểm đánh giá trung bình toàn hệ thống (`OVERALL_AVERAGE`).

## Input
- Dataset: `olist_order_reviews_dataset.csv`
- HDFS Input Path: `hdfs://namenode:9000/data/olist/olist_order_reviews_dataset.csv`

## Input Schema
```
review_id, order_id, review_score, review_comment_title, review_comment_message, review_creation_date, review_answer_timestamp
```

## Mapper (`mapper.py`)
### Input
Dòng bản ghi review từ `stdin`.
### Logic
1. Parse CSV bằng `csv.reader` để xử lý chuỗi ký tự bình luận có dấu phẩy và xuống dòng.
2. Bỏ qua dòng tiêu đề (`row[0] == "review_id"`).
3. Kiểm tra trường `review_score`: phải là ký tự số nguyên trong miền `[1, 5]`.
4. Phát sinh 2 cặp khóa-giá trị:
   - Cặp 1 (Tần suất từng mức điểm): `SCORE_<N>\t1`
   - Cặp 2 (Tổng hợp điểm trung bình): `OVERALL_AVERAGE\t<N>,1`
### Output Key
`SCORE_1` ... `SCORE_5` hoặc `OVERALL_AVERAGE`
### Output Value
`1` (cho tần suất) hoặc `<N>,1` (cho điểm trung bình)

## Shuffle & Sort (Hadoop Framework)
### Grouping Key
`SCORE_1`..`SCORE_5` và `OVERALL_AVERAGE`
### What Hadoop Does
1. Sắp xếp thứ tự các khóa theo bảng chữ cái.
2. Gom nhóm toàn bộ các giá trị của `OVERALL_AVERAGE` về cùng một reducer task.
3. Gom nhóm toàn bộ các giá trị của từng điểm số:
   `SCORE_5 -> [1, 1, 1, ...]`

## Reducer (`reducer.py`)
### Input
Dòng khóa-giá trị đã sắp xếp từ `stdin`.
### Logic
1. Nếu khóa dạng `SCORE_X`: cộng dồn biến đếm và xuất số lượng đánh giá của mức điểm đó.
2. Nếu khóa dạng `OVERALL_AVERAGE`: cộng dồn tổng điểm (`sum += score`) và tổng số đánh giá (`total += count`), sau đó tính điểm trung bình: `avg = sum / total`.
### Output Schema
```
SCORE_1          <count>
SCORE_2          <count>
SCORE_3          <count>
SCORE_4          <count>
SCORE_5          <count>
OVERALL_AVERAGE  <avg_score>   <total_reviews>
```

## HDFS Output
- HDFS Output Path: `hdfs://namenode:9000/output/job05_reviews`

## Execution Command
```bash
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
  -D mapreduce.framework.name=local \
  -input hdfs://namenode:9000/data/olist/olist_order_reviews_dataset.csv \
  -output hdfs://namenode:9000/output/job05_reviews \
  -mapper "python3 /app/src/jobs/job05_reviews/mapper.py" \
  -reducer "python3 /app/src/jobs/job05_reviews/reducer.py"
```
