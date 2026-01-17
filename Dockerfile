FROM python:3.11-alpine

RUN apk add --no-cache \
    curl \
    tzdata \
    py3-pip \
    cronie \
    && cp /usr/share/zoneinfo/America/Argentina/Buenos_Aires /etc/localtime \
    && echo "America/Argentina/Buenos_Aires" > /etc/timezone

# Instalar CLI oficial de Ookla
RUN curl -Lo speedtest.tgz https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-x86_64.tgz && \
    tar -xvzf speedtest.tgz && \
    mv speedtest /usr/bin/speedtest && \
    chmod +x /usr/bin/speedtest && \
    rm speedtest.tgz

RUN /usr/bin/speedtest --accept-license --accept-gdpr > /dev/null

RUN pip install --no-cache-dir requests pytz supabase dnspython

RUN test -e /usr/bin/python || ln -s /usr/bin/python3 /usr/bin/python
RUN mkdir -p /var/log

WORKDIR /app
COPY speedtest.py .
COPY entrypoint.sh .

RUN chmod +x /app/speedtest.py /app/entrypoint.sh

# Cron cada 30 minutos
RUN echo "0,30 * * * * . /app/.env.sh && /usr/local/bin/python /app/speedtest.py >> /var/log/cron.log 2>&1" > /etc/crontabs/root

CMD ["/app/entrypoint.sh"]
