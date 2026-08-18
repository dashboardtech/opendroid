#!/bin/zsh
# Build OpenDroid fork on the Mac Mini. Never run this on moshi.
set -euo pipefail
ROOT="${0:A:h:h}"
# script lives in scripts/; repo root is parent
export JAVA_HOME="/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
export ANDROID_HOME="${HOME}/Library/Android/sdk"
export PATH="$JAVA_HOME/bin:$PATH"
TOKEN_FILE="$ROOT/.mcp_token"
if [[ ! -f $TOKEN_FILE ]]; then
  echo "missing $TOKEN_FILE" >&2
  exit 1
fi
export MCP_ACCESS_TOKEN="$(tr -d " \n" < "$TOKEN_FILE")"
printf "sdk.dir=%s\n" "$ANDROID_HOME" > "$ROOT/local.properties"
cd "$ROOT"
exec ./gradlew assembleDebug \
  -PMCP_ACCESS_TOKEN="$MCP_ACCESS_TOKEN" \
  -PMCP_BIND_ADDRESS=0.0.0.0 \
  --no-daemon \
  "$@"
