"""H6.4: caracterización offline de los campos de consumo en los streams conservados de D071.

Solo lectura y solo biblioteca estándar, independiente de la implementación del harness. Abre cada SQLite
con `immutable=1` (sin escribir WAL/SHM), verifica tamaño y SHA-256 de cada stdout contra la captura sellada
y emite únicamente nombres de campo, tipos, recuentos y comprobaciones booleanas: ningún texto, prompt,
ruta de trabajo, identificador de sesión ni dato de límites de uso.

    python3 -I docs/discovery/H6.4_STREAM_CATALOG.py /private/tmp/harness-provider-matrix-6 > salida.json
"""
import collections
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

CLAUDE = ('input_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens', 'output_tokens')


def shape(value, depth=0):
    if isinstance(value, dict):
        return {key: shape(item, depth + 1) for key, item in sorted(value.items())} if depth < 3 else 'object'
    if isinstance(value, list):
        return 'list'
    return type(value).__name__


def merge(catalog, value):
    for key, item in value.items():
        if isinstance(item, dict) and isinstance(catalog.get(key), dict):
            merge(catalog[key], item)
        else:
            catalog.setdefault(key, item)


def claude(events):
    result = [e for e in events if e['type'] == 'result']
    terminal = result[-1]
    messages, repeats, tools = [], collections.Counter(), collections.Counter()
    snapshots = {}
    for event in events:
        inner = event.get('event') if event['type'] == 'stream_event' else None
        if inner and inner.get('type') == 'message_start':
            messages.append(dict(inner['message']['usage']))
        elif inner and inner.get('type') == 'message_delta':
            messages[-1].update({k: v for k, v in inner['usage'].items() if k in CLAUDE})
        elif event['type'] == 'assistant':
            repeats[event['message']['id']] += 1
            snapshots[event['message']['id']] = event['message']['usage']['output_tokens']
            for block in event['message'].get('content') or ():
                if block.get('type') == 'tool_use':
                    tools[block['id']] += 1
    summed = {key: sum(m.get(key, 0) for m in messages) for key in CLAUDE}
    usage, model_usage = terminal['usage'], terminal['modelUsage']
    per_model = {key: sum(m[name] for m in model_usage.values())
                 for key, name in zip(CLAUDE, ('inputTokens', 'cacheReadInputTokens', 'cacheCreationInputTokens',
                                               'outputTokens'))}
    return {
        'terminal_events': len(result),
        'assistant_events': sum(repeats.values()), 'assistant_messages': len(repeats),
        'assistant_message_repeated': max(repeats.values()) > 1,
        'message_start_events': len(messages),
        'terminal_usage_equals_sum_of_message_deltas': all(usage[k] == summed[k] for k in CLAUDE),
        'assistant_output_is_partial_snapshot': sum(snapshots.values()) < usage['output_tokens'],
        'model_usage_sum_equals_usage': all(usage[k] == per_model[k] for k in CLAUDE),
        'models_reported': len(model_usage),
        'thinking_le_output': usage['output_tokens_details']['thinking_tokens'] <= usage['output_tokens'],
        'tool_use_ids_unique': all(n == 1 for n in tools.values()), 'tool_uses': len(tools),
        'num_turns_present': type(terminal.get('num_turns')) is int,
        'duration_api_ms_present': type(terminal.get('duration_api_ms')) is int,
        'total_cost_usd_present': isinstance(terminal.get('total_cost_usd'), float),
        'permission_denials_list': isinstance(terminal.get('permission_denials'), list),
        'effort_reported': any('effort' in e for e in events),
        'subagent_messages': any(e.get('parent_tool_use_id') for e in events),
    }


def codex(events):
    terminals = [e for e in events if e['type'] in ('turn.completed', 'turn.failed')]
    usage = terminals[-1].get('usage') or {}
    items = collections.Counter(e['item']['type'] for e in events if e['type'] == 'item.completed')
    return {
        'terminal_events': len(terminals),
        'item_types': dict(sorted(items.items())),
        'cached_le_input': usage['cached_input_tokens'] <= usage['input_tokens'],
        'reasoning_le_output': usage['reasoning_output_tokens'] <= usage['output_tokens'],
        'cache_write_zero': usage['cache_write_input_tokens'] == 0,
        'model_effort_cost_duration_reported': any(
            key in e for e in events for key in ('model', 'effort', 'total_cost_usd', 'duration_ms', 'num_turns')),
    }


def main(area):
    out = {'area': 'D071 matrix-6 (ruta local, sin contenidos)', 'streams': [], 'catalog': {}}
    for database in sorted(Path(area).glob('*/state/harness.sqlite3')):
        db = sqlite3.connect(f'file:{database}?immutable=1', uri=True)
        rows = db.execute('SELECT p.spec, p.capture, a.request_json, a.number FROM managed_processes p '
                          'JOIN managed_attempts a ON a.id = p.attempt_id ORDER BY a.number').fetchall()
        db.close()
        for spec, capture, request, number in rows:
            spec, capture = json.loads(spec), json.loads(capture)
            artifact = capture['artifacts']['stdout']
            data = Path(artifact['path']).read_bytes()
            verified = len(data) == artifact['size'] and hashlib.sha256(data).hexdigest() == artifact['sha256']
            events = [json.loads(line) for line in data.splitlines() if line.strip()]
            kinds = collections.Counter(
                e['type'] + ('/' + e['subtype'] if isinstance(e.get('subtype'), str) else '') for e in events)
            provider = spec['provider']
            for event in events:
                key = f"{provider}:{event['type']}"
                if event['type'] in ('result', 'turn.completed', 'turn.failed', 'rate_limit_event'):
                    merge(out['catalog'].setdefault(key, {}), shape(event) if event['type'] != 'rate_limit_event'
                          else {'rate_limit_info': 'object (no se conserva)'})
            out['streams'].append({
                'pairing': database.parent.parent.name, 'attempt': number, 'role': json.loads(request)['role'],
                'provider': provider, 'sha256_verified': verified, 'event_types': dict(sorted(kinds.items())),
                'checks': claude(events) if provider == 'claude' else codex(events)})
    return out


if __name__ == '__main__':
    json.dump(main(sys.argv[1]), sys.stdout, indent=1, sort_keys=True, ensure_ascii=False)
    sys.stdout.write('\n')
