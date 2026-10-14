"""H6.4 (D072 §9): métricas por intento con procedencia por campo. Biblioteca estándar, sin E/S.

Catálogo `metrics-1`, caracterizado offline con los streams conservados de D071
(`docs/discovery/H6.4_METRICS.md`). Procedencias: `requested` (selección congelada), `reported` (lo emite
el proveedor), `derived` (calculado por el harness desde eventos reportados), `measured` (reloj del
harness) y `absent`. Un null nunca es cero.

Reglas contra el doble conteo: el uso del terminal es el acumulado de la invocación y nunca se suma con
el uso por mensaje, que solo se usa, deduplicado, cuando no hay terminal. Los eventos `assistant` de
Claude repiten el mismo mensaje y traen una instantánea parcial de la salida: no cuentan tokens. Los
tokens de razonamiento son un subconjunto de la salida. Nada de `rate_limit_event` se conserva: la cuota
no se deduce.
"""

import json
import math

CATALOG = 'metrics-1'
# Normalización de la captura del terminal. Sin clave en los metadatos: `terminal-1` (anterior a H6.4).
CAPTURE = 'terminal-2'
LEGACY_CAPTURE = 'terminal-1'
TOKENS = ('input_tokens', 'cache_read_tokens', 'cache_write_tokens', 'output_tokens', 'reasoning_tokens')
# Campos del terminal que `terminal-2` añade a los ya capturados por `terminal-1`.
TERMINAL_FIELDS = ('usage', 'modelUsage', 'duration_ms', 'total_cost_usd', 'permission_denials')
TERMINAL_FIELDS_2 = ('num_turns', 'duration_api_ms')

CLAUDE_USAGE = {'input_tokens': 'input_tokens', 'cache_read_tokens': 'cache_read_input_tokens',
                'cache_write_tokens': 'cache_creation_input_tokens', 'output_tokens': 'output_tokens'}
CLAUDE_MODEL_USAGE = {'input_tokens': 'inputTokens', 'cache_read_tokens': 'cacheReadInputTokens',
                      'cache_write_tokens': 'cacheCreationInputTokens', 'output_tokens': 'outputTokens',
                      'reasoning_tokens': 'thinkingTokens'}
CODEX_USAGE = {'input_tokens': 'input_tokens', 'cache_read_tokens': 'cached_input_tokens',
               'cache_write_tokens': 'cache_write_input_tokens', 'output_tokens': 'output_tokens',
               'reasoning_tokens': 'reasoning_output_tokens'}
# Claude informa la entrada sin la caché; Codex la incluye (caché leída ⊆ entrada en las 6 muestras D071).
INPUT_SEMANTICS = {'claude': 'excludes_cache', 'codex': 'includes_cache_read'}
# Elementos de Codex que no son herramientas; el resto de tipos completados cuentan como herramienta.
CODEX_NON_TOOLS = frozenset({'agent_message', 'reasoning', 'error'})
VERDICT_ROLES = frozenset({'reviewer', 'phase'})


def count(value):
    """Entero no negativo reportado; cualquier otra cosa es ausencia, nunca cero."""
    return value if type(value) is int and value >= 0 else None


def amount(value):
    if type(value) in (int, float) and math.isfinite(value) and value >= 0:
        return float(value)
    return None


def _usage(data, mapping):
    if not isinstance(data, dict):
        return None
    return {name: count(data.get(key)) for name, key in mapping.items()}


class StreamMetrics:
    """Contadores derivados de un stream JSONL de agente; el mismo cálculo en la captura y en el relleno."""

    def __init__(self, provider):
        self.provider = provider
        self.messages = []   # Claude: uso por mensaje, message_start actualizado por message_delta (acumulado).
        self.tool_ids = {}   # nombre o tipo → ids vistos (los eventos de Claude repiten el mismo mensaje).
        self.anonymous = {}  # herramientas sin id: se cuentan por evento.
        self.items = {}      # Codex: item.completed por tipo, una vez por id.
        self.item_ids = set()
        self.terminal = {}   # Campos del último terminal, incluidos los de terminal-2.

    def _tool(self, name, ident):
        if not isinstance(name, str) or not name:
            return
        if isinstance(ident, str) and ident:
            self.tool_ids.setdefault(name, set()).add(ident)
        else:
            self.anonymous[name] = self.anonymous.get(name, 0) + 1

    def event(self, event, *, terminal=False):
        kind = event.get('type')
        if self.provider == 'codex':
            item = event.get('item')
            if kind == 'item.completed' and isinstance(item, dict) and isinstance(item.get('type'), str):
                ident = item.get('id')
                if not (isinstance(ident, str) and ident in self.item_ids):
                    if isinstance(ident, str):
                        self.item_ids.add(ident)
                    self.items[item['type']] = self.items.get(item['type'], 0) + 1
                    if item['type'] not in CODEX_NON_TOOLS:
                        self.anonymous[item['type']] = self.anonymous.get(item['type'], 0) + 1
        elif kind == 'stream_event' and isinstance(event.get('event'), dict):
            inner = event['event']
            if inner.get('type') == 'message_start' and isinstance(inner.get('message'), dict):
                self.messages.append(_usage(inner['message'].get('usage'), CLAUDE_USAGE)
                                     or dict.fromkeys(CLAUDE_USAGE))
            elif inner.get('type') == 'message_delta' and self.messages:
                # Uso acumulado del mensaje en curso: sustituye, nunca suma.
                delta = _usage(inner.get('usage'), CLAUDE_USAGE) or {}
                self.messages[-1] = {name: delta[name] if delta.get(name) is not None else value
                                     for name, value in self.messages[-1].items()}
        elif kind == 'assistant' and isinstance(event.get('message'), dict):
            for block in event['message'].get('content') or ():
                if isinstance(block, dict) and block.get('type') == 'tool_use':
                    self._tool(block.get('name'), block.get('id'))
        if terminal:
            self.terminal = {key: event[key] for key in TERMINAL_FIELDS + TERMINAL_FIELDS_2 if key in event}

    def summary(self) -> dict:
        tools = {name: len(ids) for name, ids in self.tool_ids.items()}
        for name, value in self.anonymous.items():
            tools[name] = tools.get(name, 0) + value
        usage = None
        if self.messages:
            usage = {name: (sum(m[name] for m in self.messages) if all(m[name] is not None for m in self.messages)
                            else None) for name in CLAUDE_USAGE}
        return {'format': CAPTURE, 'messages': len(self.messages) if self.provider == 'claude' else None,
                'message_usage': usage, 'tools': dict(sorted(tools.items())),
                'items': dict(sorted(self.items.items())) if self.provider == 'codex' else None}


TERMINALS = {'codex': frozenset({'turn.completed', 'turn.failed'}), 'claude': frozenset({'result'})}


def replay(provider: str, data: bytes) -> dict:
    """Relectura de un stdout sellado (relleno): mismas reglas que la captura, sin efectos."""
    metrics = StreamMetrics(provider)
    for line in data.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line.decode('utf-8'), parse_constant=_reject)
        except (UnicodeDecodeError, ValueError):
            continue
        if isinstance(event, dict) and isinstance(event.get('type'), str):
            metrics.event(event, terminal=event['type'] in TERMINALS.get(provider, ()))
    return {'summary': metrics.summary(), 'terminal': metrics.terminal}


def _reject(value):
    raise ValueError(f'Nonfinite JSON: {value}')


def _loads(value):
    if not isinstance(value, str):
        return None
    try:
        return json.loads(value)
    except ValueError:
        return None


def attempt_metrics(*, request: dict, result: dict | None, status: str, spec: dict | None, executor_round: int,
                    stream: dict | None = None) -> dict:
    """Fila de métricas de un intento resuelto. `stream`: relectura verificada (relleno) con `summary` y
    `terminal`; sin ella se usan solo los metadatos sellados del intento."""
    provider = spec.get('provider') if isinstance(spec, dict) else None
    meta = _loads((result or {}).get('metadata_json'))
    meta = meta if isinstance(meta, dict) else {}
    observed = meta.get('observed') if isinstance(meta.get('observed'), dict) else {}
    derived = meta.get('stream_metrics') if isinstance(meta.get('stream_metrics'), dict) else None
    if stream is not None:
        # Solo completa lo que la captura sellada no tenía; nunca reemplaza un valor sellado.
        observed = {**stream['terminal'], **observed}
        derived = derived or stream['summary']
    provenance = {'requested_model': 'requested', 'requested_effort': 'requested'}

    def put(name, value, label):
        provenance[name] = label if value is not None else 'absent'
        return value

    mapping = {'claude': CLAUDE_USAGE, 'codex': CODEX_USAGE}.get(provider)
    usage = observed.get('usage')
    tokens, accounting = dict.fromkeys(TOKENS), None
    if mapping and isinstance(usage, dict):
        tokens = {**tokens, **_usage(usage, mapping)}
        if provider == 'claude':
            details = usage.get('output_tokens_details')
            tokens['reasoning_tokens'] = count(details.get('thinking_tokens')) if isinstance(details, dict) else None
        accounting = 'terminal' if any(value is not None for value in tokens.values()) else None
    elif provider == 'claude' and derived and isinstance(derived.get('message_usage'), dict):
        tokens = {**tokens, **{name: count(derived['message_usage'].get(name)) for name in CLAUDE_USAGE}}
        accounting = 'messages' if any(value is not None for value in tokens.values()) else None
    label = {'terminal': 'reported', 'messages': 'derived'}.get(accounting)
    row = {name: put(name, value, label) for name, value in tokens.items()}
    semantics = INPUT_SEMANTICS.get(provider) if accounting else None
    uncached = None
    if semantics == 'excludes_cache':
        uncached = row['input_tokens']
    elif semantics == 'includes_cache_read' and row['input_tokens'] is not None and row['cache_read_tokens'] is not None \
            and row['cache_read_tokens'] <= row['input_tokens']:
        uncached = row['input_tokens'] - row['cache_read_tokens']
    row['uncached_input_tokens'] = put('uncached_input_tokens', uncached, 'derived')
    total = None
    if uncached is not None and row['cache_read_tokens'] is not None and row['output_tokens'] is not None:
        if semantics == 'excludes_cache' and row['cache_write_tokens'] is not None:
            total = uncached + row['cache_read_tokens'] + row['cache_write_tokens'] + row['output_tokens']
        elif semantics == 'includes_cache_read' and row['cache_write_tokens'] in (0, None):
            # Codex: escritura de caché nunca observada distinta de cero; no se sabe si va dentro de la entrada.
            total = uncached + row['cache_read_tokens'] + row['output_tokens']
    row['total_tokens'] = put('total_tokens', total, 'derived')

    models = []
    if provider == 'claude' and isinstance(observed.get('modelUsage'), dict):
        for model, data in sorted(observed['modelUsage'].items()):
            if isinstance(model, str) and isinstance(data, dict):
                models.append({'model': model, **_usage(data, CLAUDE_MODEL_USAGE), 'cost_usd': amount(data.get('costUSD'))})
    put('models', models or None, 'reported')
    reported = [item['model'] for item in models]
    if not reported and isinstance(observed.get('message_models'), list):
        reported = sorted(m for m in observed['message_models'] if isinstance(m, str))
    if not reported and isinstance(observed.get('model'), str):
        reported = [observed['model']]
    effort = observed.get('effort') if isinstance(observed.get('effort'), str) else None

    turns, turns_label = count(observed.get('num_turns')), 'reported'
    if turns is None and provider == 'codex' and derived and isinstance(derived.get('items'), dict):
        turns, turns_label = sum(v for v in derived['items'].values() if count(v) is not None), 'derived'
    tools = derived.get('tools') if derived and isinstance(derived.get('tools'), dict) else None
    denials = observed.get('permission_denials')
    wall = meta.get('wall_duration_seconds')
    payload = _loads((result or {}).get('payload_json'))
    verdict = payload.get('verdict') if request['role'] in VERDICT_ROLES and isinstance(payload, dict) else None
    error = (result or {}).get('error')
    selection = request.get('selection') or {}
    row.update({
        'provider': provider,
        'adapter_version': spec.get('adapter_version') if isinstance(spec, dict) else None,
        'cli_version': spec.get('cli_version') if isinstance(spec, dict) else None,
        'requested_model': selection.get('model'), 'requested_effort': selection.get('effort'),
        'reported_models': put('reported_models', reported or None, 'reported'),
        'reported_effort': put('reported_effort', effort, 'reported'),
        'accounting': accounting, 'input_semantics': semantics,
        'turns': put('turns', turns, turns_label),
        'tools': put('tools', tools, 'derived'),
        'tool_calls': put('tool_calls', sum(tools.values()) if tools is not None else None, 'derived'),
        'permission_denials': put('permission_denials', len(denials) if isinstance(denials, list) else None, 'reported'),
        'wall_ms': put('wall_ms', round(wall * 1000) if amount(wall) is not None else None, 'measured'),
        'duration_ms': put('duration_ms', count(observed.get('duration_ms')), 'reported'),
        'api_duration_ms': put('api_duration_ms', count(observed.get('duration_api_ms')), 'reported'),
        'cost_usd': put('cost_usd', amount(observed.get('total_cost_usd')), 'reported'),
        'verdict': put('verdict', verdict if isinstance(verdict, str) else None, 'reported'),
        'status': status, 'error': error[:1000] if isinstance(error, str) else None, 'executor_round': executor_round,
        'normalization': (meta.get('normalization') or LEGACY_CAPTURE) if meta else None,
        'models': models, 'provenance': provenance,
    })
    return row
