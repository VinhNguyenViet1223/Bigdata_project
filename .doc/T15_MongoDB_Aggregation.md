\# T15 - MongoDB Aggregation



\## Mục tiêu

Thực hiện các truy vấn MongoDB Aggregation tương đương với các truy vấn SQL trên bộ dữ liệu Olist.



\---



\## Query 1 - Tổng giá trị thanh toán



\### SQL tương đương

SELECT SUM(payment\_value)

FROM order\_payments;



\### MongoDB

db.order\_payments.aggregate(\[

&#x20; {

&#x20;   $group: {

&#x20;     \_id: null,

&#x20;     total\_revenue: { $sum: "$payment\_value" }

&#x20;   }

&#x20; }

])



\### Kết quả

total\_revenue: 16008872.12



\---



\## Query 2 - Giá trị thanh toán theo phương thức



\### MongoDB

db.order\_payments.aggregate(\[

&#x20; {

&#x20;   $group: {

&#x20;     \_id: "$payment\_type",

&#x20;     total\_revenue: { $sum: "$payment\_value" },

&#x20;     payment\_count: { $sum: 1 }

&#x20;   }

&#x20; },

&#x20; {

&#x20;   $sort: {

&#x20;     total\_revenue: -1

&#x20;   }

&#x20; }

])



\### Kết quả

\- credit\_card: 12542084.19 - 76795 payments

\- boleto: 2869361.27 - 19784 payments

\- voucher: 379436.87 - 5775 payments

\- debit\_card: 217989.79 - 1529 payments

\- not\_defined: 0 - 3 payments



\---



\## Query 3 - Số đơn hàng theo trạng thái



\### MongoDB

db.orders.aggregate(\[

&#x20; {

&#x20;   $group: {

&#x20;     \_id: "$order\_status",

&#x20;     order\_count: { $sum: 1 }

&#x20;   }

&#x20; },

&#x20; {

&#x20;   $sort: {

&#x20;     order\_count: -1

&#x20;   }

&#x20; }

])



\### Kết quả

\- delivered: 96478

\- shipped: 1107

\- canceled: 625

\- unavailable: 609

\- invoiced: 314

\- processing: 301

\- created: 5

\- approved: 2



Tổng: 99441 orders



\---



\## Query 4 - Top 10 seller theo doanh thu



\### MongoDB

db.order\_items.aggregate(\[

&#x20; {

&#x20;   $group: {

&#x20;     \_id: "$seller\_id",

&#x20;     total\_sales: { $sum: "$price" },

&#x20;     item\_count: { $sum: 1 }

&#x20;   }

&#x20; },

&#x20; {

&#x20;   $sort: {

&#x20;     total\_sales: -1

&#x20;   }

&#x20; },

&#x20; {

&#x20;   $limit: 10

&#x20; }

])



\### Seller đứng đầu

\- seller\_id: 4869f7a5dfa277a7dca6462dcf3b52b2

\- total\_sales: 229472.63

\- item\_count: 1156



\---



\## Query 5 - Top 10 category theo doanh thu



Sử dụng `$lookup` để nối `order\_items` với `products` thông qua `product\_id`.



\### MongoDB

db.order\_items.aggregate(\[

&#x20; {

&#x20;   $group: {

&#x20;     \_id: "$product\_id",

&#x20;     total\_sales: { $sum: "$price" },

&#x20;     items\_sold: { $sum: 1 }

&#x20;   }

&#x20; },

&#x20; {

&#x20;   $lookup: {

&#x20;     from: "products",

&#x20;     localField: "\_id",

&#x20;     foreignField: "product\_id",

&#x20;     as: "product"

&#x20;   }

&#x20; },

&#x20; {

&#x20;   $unwind: "$product"

&#x20; },

&#x20; {

&#x20;   $group: {

&#x20;     \_id: "$product.product\_category\_name",

&#x20;     total\_sales: { $sum: "$total\_sales" },

&#x20;     items\_sold: { $sum: "$items\_sold" }

&#x20;   }

&#x20; },

&#x20; {

&#x20;   $sort: {

&#x20;     total\_sales: -1

&#x20;   }

&#x20; },

&#x20; {

&#x20;   $limit: 10

&#x20; }

])



\### Kết quả

1\. beleza\_saude - 1258681.34 - 9670 items

2\. relogios\_presentes - 1205005.68 - 5991 items

3\. cama\_mesa\_banho - 1036988.68 - 11115 items

4\. esporte\_lazer - 988048.97 - 8641 items

5\. informatica\_acessorios - 911954.32 - 7827 items

6\. moveis\_decoracao - 729762.49 - 8334 items

7\. cool\_stuff - 635290.85 - 3796 items

8\. utilidades\_domesticas - 632248.66 - 6964 items

9\. automotivo - 592720.11 - 4235 items

10\. ferramentas\_jardim - 485256.46 - 4347 items



\---



\## Kết luận



Đã thực hiện các thao tác MongoDB Aggregation:



\- `$group`

\- `$sum`

\- `$sort`

\- `$limit`

\- `$lookup`

\- `$unwind`



Các truy vấn tương ứng với các thao tác SQL như:



\- GROUP BY

\- SUM

\- COUNT

\- ORDER BY

\- LIMIT

\- JOIN

