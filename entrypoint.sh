#!/bin/sh

# Export environment variables to a file so cron can use them
printenv | grep -E "^(SUPABASE|TELEGRAM|ERROR_REPORTING|SPEED_THRESHOLD)" | sed 's/^\(.*\)$/export \1/g' > /app/.env.sh

# Run speedtest immediately on startup
/usr/local/bin/python /app/speedtest.py >> /var/log/cron.log 2>&1

# Start cron in foreground
exec crond -f
