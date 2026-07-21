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

# --- Tests + cobertura ---
if [ "${TESTS_OUTCOME:-}" = "success" ]; then
  tests_emoji="✅"
elif [ "${TESTS_OUTCOME:-}" = "failure" ]; then
  tests_emoji="❌"
else
  tests_emoji="❔"
fi
tests_summary="${TESTS_SUMMARY:-sin resumen}"
coverage_line=""
if [ -n "${COVERAGE_PCT:-}" ]; then
  coverage_line=" · Cobertura: ${COVERAGE_PCT}%"
fi

# --- Bandit ---
if [ "${BANDIT_OUTCOME:-}" = "success" ]; then
  bandit_emoji="✅"; bandit_text="sin hallazgos medium/high"
elif [ "${BANDIT_OUTCOME:-}" = "failure" ]; then
  bandit_emoji="❌"; bandit_text="con hallazgos medium/high"
else
  bandit_emoji="❔"; bandit_text="no se ejecutó"
fi

# --- pip-audit ---
if [ "${PIP_AUDIT_OUTCOME:-}" = "success" ]; then
  pip_emoji="✅"; pip_text="sin vulnerabilidades conocidas"
elif [ "${PIP_AUDIT_OUTCOME:-}" = "failure" ]; then
  pip_emoji="❌"; pip_text="con vulnerabilidades conocidas"
else
  pip_emoji="❔"; pip_text="no se ejecutó"
fi

# --- npm audit ---
if [ "${NPM_AUDIT_OUTCOME:-}" = "success" ]; then
  npm_emoji="✅"; npm_text="sin vulnerabilidades HIGH/CRITICAL"
elif [ "${NPM_AUDIT_OUTCOME:-}" = "failure" ]; then
  npm_emoji="❌"; npm_text="con vulnerabilidades HIGH/CRITICAL"
else
  npm_emoji="❔"; npm_text="no se ejecutó"
fi

MSG="$(cat <<EOF
🔀 <b>Merge a $(printf '%s' "${BRANCH:-?}" | esc) — Master Gateway</b>
<code>${short_sha}</code> · $(printf '%s' "${COMMIT_MESSAGE:-}" | esc)

${tests_emoji} <b>Tests (pytest)</b>: $(printf '%s' "$tests_summary" | esc)${coverage_line}
${bandit_emoji} <b>Bandit (SAST)</b>: ${bandit_text}
${pip_emoji} <b>pip-audit</b>: ${pip_text}
${npm_emoji} <b>npm audit</b>: ${npm_text}

🔗 <a href="${RUN_URL:-}">Ver ejecución en GitHub Actions</a>
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
