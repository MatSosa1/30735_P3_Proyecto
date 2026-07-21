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

blocks=""

# --- Tests + cobertura (solo si esta etapa los corrió) ---
if [ -n "${TESTS_OUTCOME:-}" ]; then
  if [ "${TESTS_OUTCOME}" = "success" ]; then
    tests_emoji="✅"
  elif [ "${TESTS_OUTCOME}" = "failure" ]; then
    tests_emoji="❌"
  else
    tests_emoji="❔"
  fi
  coverage_line=""
  [ -n "${COVERAGE_PCT:-}" ] && coverage_line=" · Cobertura: ${COVERAGE_PCT}%"
  blocks="${blocks}"$'\n'"${tests_emoji} <b>Tests (pytest)</b>: $(printf '%s' "${TESTS_SUMMARY:-sin resumen}" | esc)${coverage_line}"
fi

# --- Build del frontend (solo si esta etapa lo corrió) ---
if [ -n "${FRONTEND_BUILD_OUTCOME:-}" ]; then
  if [ "${FRONTEND_BUILD_OUTCOME}" = "success" ]; then
    build_emoji="✅"; build_text="OK"
  else
    build_emoji="❌"; build_text="FALLÓ"
  fi
  blocks="${blocks}"$'\n'"${build_emoji} <b>Build frontend</b>: ${build_text}"
fi

# --- Bandit (solo si esta etapa lo corrió) ---
if [ -n "${BANDIT_OUTCOME:-}" ]; then
  if [ "${BANDIT_OUTCOME}" = "success" ]; then
    bandit_emoji="✅"; bandit_text="sin hallazgos medium/high"
  else
    bandit_emoji="❌"; bandit_text="con hallazgos medium/high"
  fi
  blocks="${blocks}"$'\n'"${bandit_emoji} <b>Bandit (SAST)</b>: ${bandit_text}"
fi

# --- pip-audit (solo si esta etapa lo corrió) ---
if [ -n "${PIP_AUDIT_OUTCOME:-}" ]; then
  if [ "${PIP_AUDIT_OUTCOME}" = "success" ]; then
    pip_emoji="✅"; pip_text="sin vulnerabilidades conocidas"
  else
    pip_emoji="❌"; pip_text="con vulnerabilidades conocidas"
  fi
  blocks="${blocks}"$'\n'"${pip_emoji} <b>pip-audit</b>: ${pip_text}"
fi

# --- npm audit (solo si esta etapa lo corrió) ---
if [ -n "${NPM_AUDIT_OUTCOME:-}" ]; then
  if [ "${NPM_AUDIT_OUTCOME}" = "success" ]; then
    npm_emoji="✅"; npm_text="sin vulnerabilidades HIGH/CRITICAL"
  else
    npm_emoji="❌"; npm_text="con vulnerabilidades HIGH/CRITICAL"
  fi
  blocks="${blocks}"$'\n'"${npm_emoji} <b>npm audit</b>: ${npm_text}"
fi

checks_line=""
[ -n "${CHECKS_LABEL:-}" ] && checks_line=$'\n'"<i>$(printf '%s' "$CHECKS_LABEL" | esc)</i>"

MSG="$(cat <<EOF
🔀 <b>Merge a $(printf '%s' "${BRANCH:-?}" | esc) — Master Gateway</b>
<code>${short_sha}</code> · $(printf '%s' "${COMMIT_MESSAGE:-}" | esc)${checks_line}
${blocks}

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
