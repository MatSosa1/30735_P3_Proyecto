#!/usr/bin/env bash
set -euo pipefail

missing=""
[ -z "${TELEGRAM_BOT_TOKEN:-}" ] && missing="${missing} TELEGRAM_BOT_TOKEN"
[ -z "${TELEGRAM_CHAT_ID:-}" ]   && missing="${missing} TELEGRAM_CHAT_ID"
if [ -n "$missing" ]; then
  echo "::warning::Falta(n) el/los secret(s):${missing}. No se notifica el inicio del pipeline (no se hace fallar el job por esto, a diferencia del resumen final)."
  exit 0
fi

esc() { sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g'; }

if [ "${EVENT_NAME:-}" = "pull_request" ] && [ -n "${PR_NUMBER:-}" ]; then
  ctx="PR #${PR_NUMBER} → ${BRANCH:-?}"
else
  ctx="push → ${BRANCH:-?}"
fi
short_sha="${COMMIT_SHA:0:7}"

MSG="$(cat <<EOF
🚀 <b>Pipeline iniciado — Master Gateway</b>
$(printf '%s' "$ctx" | esc) · <code>${short_sha}</code>

Corriendo: tests + cobertura, SonarQube Quality Gate, Bandit (SAST), Trivy (dependencias), build de frontend.

🔗 <a href="${RUN_URL:-}">Ver ejecución en GitHub Actions</a>
EOF
)"

curl -s -o /dev/null -w '%{http_code}' \
  -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
  --data-urlencode "text=${MSG}" \
  -d "parse_mode=HTML" \
  -d "disable_web_page_preview=true" > /dev/null || true

echo "Notificación de inicio enviada (best-effort, no bloquea el pipeline si falla)."
