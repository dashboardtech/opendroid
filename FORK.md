# OpenDroid — Fork Hermes (dashboardtech)

> Agente Android autónomo con cerebro 100% local (Ollama en el tailnet) y cuerpo operable a distancia vía MCP.
> Fork de [yashab-cyber/opendroid](https://github.com/yashab-cyber/opendroid) v1.0.5 — mantenido por Hermes (el agente de Frederick, @hermes).

## ¿Por qué este fork existe

Upstream v1.0.5 corre un server MCP en el teléfono con 13 herramientas (60+ acciones físicas, terminal persistente, comandos privilegiados), pero:

1. **Bindea a `127.0.0.1:8765`** — solo alcanzable con USB/adb forward
2. **El token de acceso vive cifrado en el Keystore** y ninguna UI lo muestra — imposible autenticar un harness externo

Nuestra flota necesita que **Hermes controle el teléfono por Tailscale**, sin USB. Este fork agrega exactamente eso, en 26 líneas que respetan el diseño de seguridad upstream.

## Cambios vs upstream

| Archivo | Cambio | Líneas |
|---|---|---|
| `McpServer.kt` | Bind address configurable vía env `OPENDROID_MCP_BIND` (default `127.0.0.1` idéntico a upstream) | +7 |
| `McpConfigStore.kt` | Token MCP fijo en build-time vía `MCP_ACCESS_TOKEN` gradle property (default: comportamiento upstream con token aleatorio en Keystore) | +16 |
| `app/build.gradle` | `buildConfigField` que inyecta el token | +5 |

Sin forks de comportamiento cuando no se configuran las nuevas opciones — `git diff` es idéntico a upstream salvo los 26 insertions.

### Seguridad

El check de token (`x-opendroid-token`, comparación constant-time SHA-256) sigue aplicando a **cada** request sin importar el bind address. El modelo de seguridad cambia de "loopback físico" a "boundary de red Tailscale + token":

- El puerto 8765 solo responde dentro del tailnet (WireGuard)
- Fuera del tailnet: nada. La IP 100.x no es ruteable desde internet
- Token de 32 hex chars (128 bits) generado con `secrets` — baked en el APK

**Prerequisito**: Android 9+ bloquea cleartext HTTP hacia IPs públicas; dentro del tailnet hacia 100.x el tráfico va plano pero cifrado por WireGuard en capa 3. Verificado funcionando en Galaxy A16 (Android 16).

## Compilar

```bash
# 1. JDK 21 + Android SDK (platform-tools, android-36, build-tools 36.0.0)
export JAVA_HOME=<jdk21> ANDROID_HOME=<sdk>

# 2. Token MCP (el que Hermes usará para hablarle al teléfono)
export MCP_ACCESS_TOKEN=$(cat mcp_token.txt)   # 32 hex chars, no commitear

# 3. Build debug (auto-firmado, instalable)
./gradlew assembleDebug
# APK → app/build/outputs/apk/debug/app-debug.apk
```

## Operación (Hermes → teléfono)

```bash
# Desde cualquier nodo del tailnet (ej. moshi):
curl http://100.104.144.75:8765/mcp \
  -H "x-opendroid-token: $MCP_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

El teléfono (Galaxy A16, tailnet `100.104.144.75`) corre OpenDroid con:
- Cerebro: Ollama `qwen2.5:7b-instruct-q4_K_M` en Mac Mini (`https://fredericks-mac-mini.tail9fc0a3.ts.net:11434` vía Tailscale Serve HTTPS — Android bloquea cleartext)
- Modo: MANUAL (toda acción física requiere confirmación en pantalla por ahora)

## Roadmap del fork

- [ ] Módulo Hermes MCP client (`scripts/opendroid_client.py`) — wrapper Python de las 13 herramientas
- [ ] Wake word "Hermes" (upstream usa "OpenDroid")
- [ ] Integración como herramienta nativa de Hermes Agent (mcporter/native-mcp)
- [ ] PR upstream de la UI de token (contribuir de vuelta)

## Licencia

Upstream MIT — fork bajo la misma licencia. Todo el crédito del proyecto a [yashab-cyber](https://github.com/yashab-cyber).