FROM python:3.9-alpine

RUN apk add --no-cache curl && \
    pip install --no-cache-dir speedtest-cli requests pytz

RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/America/Argentina/Buenos_Aires /etc/localtime && \
    echo "America/Argentina/Buenos_Aires" > /etc/timezone && \
    apk del tzdata

WORKDIR /app

COPY speedtest.py /app/

RUN chmod +x /app/speedtest.py

RUN echo '0,30 * * * * /usr/local/bin/python /app/speedtest.py >> /var/log/cron.log 2>&1' > /etc/crontabs/root

CMD ["crond", "-f", "-d", "8"]