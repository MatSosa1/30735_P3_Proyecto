#!/usr/bin/env bash
set -euo pipefail

missing=""
[ -z "${TELEGRAM_BOT_TOKEN:-}" ] && missing="${missing} TELEGRAM_BOT_TOKEN"
[ -z "${TELEGRAM_CHAT_ID:-}" ]   && missing="${missing} TELEGRAM_CHAT_ID"
if [ -n "$missing" ]; then
  echo "::error::Falta(n) el/los secret(s):${missing}. La notificación a Telegram es obligatoria; configúralo(s) en Settings → Secrets and variables → Actions."
  exit 1
fi

esc() { sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g'; }

short_sha="${COMMIT_SHA:0:7}"

MSG="$(cat <<EOF
🔀 <b>Merge exitoso — Master Gateway</b>
Rama: <b>$(printf '%s' "${BRANCH:-?}" | esc)</b> · <code>${short_sha}</code>
$(printf '%s' "${COMMIT_MESSAGE:-}" | esc)

🔗 <a href="${RUN_URL:-}">Ver commit en GitHub</a>
EOF
)"

send() {
  curl -s -o /tmp/tg_branch_resp.json -w '%{http_code}' \
    -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
    --data-urlencode "text=${MSG}" \
    -d "parse_mode=HTML" \
    -d "disable_web_page_preview=true" || echo "000"
}

http_code=""
for attempt in 1 2 3; do
  http_code="$(send)"
  [ "$http_code" = "200" ] && break
  echo "::warning::Intento ${attempt}/3 de enviar a Telegram falló (HTTP ${http_code}): $(cat /tmp/tg_branch_resp.json 2>/dev/null || true)"
  sleep 3
done

if [ "$http_code" != "200" ]; then
  echo "::error::No se pudo enviar la notificación a Telegram tras 3 intentos (HTTP ${http_code})."
  exit 1
fi
echo "Notificación de merge enviada a Telegram."
