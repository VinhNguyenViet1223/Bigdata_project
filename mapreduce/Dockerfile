FROM python:3.11-slim

WORKDIR /app

COPY mapper ./mapper
COPY reducer ./reducer

RUN chmod +x ./mapper/order_status_mapper.py
RUN chmod +x ./reducer/order_status_reducer.py

CMD ["bash"]