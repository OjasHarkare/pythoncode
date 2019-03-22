FROM python:2.7-alpine
WORKDIR /app
COPY ./app/* /app/
RUN apk add alpine-sdk
RUN pip install requests html2text flask gunicorn[eventlet]
WORKDIR /app
# ENTRYPOINT ["python"]
# CMD ["main.py"]
EXPOSE 9400
CMD ["gunicorn", "--config", "./gunicorn_config.py", "main:app"]
