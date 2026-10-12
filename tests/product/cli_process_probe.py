"""Synthetic executable for H2.3; no agent, authentication or network."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import tomllib

provider, mode = sys.argv[1:3]
if '--version' in sys.argv:
    print(('codex-cli 0.162.1' if mode == 'version_new' else 'codex-cli 0.161.0') if provider == 'codex' else '2.1.295 (Claude Code)')
    sys.exit(0)
if '--help' in sys.argv:
    print('synthetic help' if mode == 'incompatible_help' else
          '--json --model --sandbox --ephemeral --ignore-user-config --ignore-rules --strict-config '
          '--print --output-format --verbose --include-partial-messages --no-session-persistence '
          '--session-id --effort --permission-mode --permission-prompts --tools --allowedTools '
          '--strict-mcp-config --mcp-config --setting-sources --settings --disable-slash-commands --no-chrome')
    sys.exit(0)
prompt = sys.stdin.read()
record = os.environ.get('PROBE_RECORD')
if record:
    with open(record, 'a') as log:
        log.write(json.dumps({'argv': sys.argv[3:], 'cwd': os.getcwd(), 'prompt': prompt,
                              'explicit': os.environ.get('PROBE_EXPLICIT'), 'pid': os.getpid()}) + '\n')
if provider == 'codex':
    # Characterize CLI configuration semantics independently of the adapter.
    # Help/version do not certify the validity of an invocation's overrides.
    args = sys.argv[3:]
    overrides = [args[index + 1] for index, value in enumerate(args) if value == '-c']
    config = tomllib.loads('\n'.join(overrides))
    reserved = {'openai', 'ollama', 'lmstudio'} & config.get('model_providers', {}).keys()
    if reserved:
        print('Synthetic config error: model_providers contains reserved built-in provider IDs: '
              + ', '.join(sorted(reserved)), file=sys.stderr)
        sys.exit(1)
else:
    # Independent contract: the CLI requires a wrapper containing a server map,
    # not an empty top-level object. Reject before emitting simulated inference.
    args = sys.argv[3:]
    config = json.loads(args[args.index('--mcp-config') + 1])
    if not isinstance(config, dict) or not isinstance(config.get('mcpServers'), dict):
        print('Synthetic config error: mcpServers: expected record', file=sys.stderr)
        sys.exit(1)
if mode == 'invalid':
    print('invalid JSONL', flush=True)
elif mode == 'utf8':
    os.write(1, b'{"type":"stream_event","text":"\xc3')
    sys.exit(0)
elif mode == 'partial':
    os.write(1, b'{"type":"res')
    sys.exit(0)
elif mode == 'no_terminal':
    print('{"type":"future.event","unknown":null}', flush=True)
    sys.exit(0)
elif mode == 'hang' or mode == 'child':
    if mode == 'child':
        child = subprocess.Popen([sys.executable, '-c',
            'import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)'])
        def reap(signum, frame):
            child.kill()
            child.wait()
            sys.exit(143)
        signal.signal(signal.SIGTERM, reap)
        Path(os.environ['PROBE_CHILD']).write_text(str(child.pid))
    print('{"type":"stream_event","event":{"delta":{"text":"partial"}}}', flush=True)
    time.sleep(60)
    sys.exit(0)
if mode == 'flow' and provider == 'codex':
    if prompt.startswith('Plan exactly'):
        payload = {'task_id':'P001-T001','phase_id':'P001','title':'Synthetic task',
            'objective':'Preserve synthetic content','executor_prompt':'Return synthetic summary',
            'allowed_paths':['app/**'],'forbidden_paths':[], 'acceptance_criteria':['Content remains valid'],
            'validation_commands':['test-runner check'], 'executor_selection':{
                'model':'synthetic-executor','effort':'medium','reason':'Explicit synthetic policy'}}
    else:
        payload = {'task_id':'P001-T001','verdict':'ACCEPT','findings':[], 'blocking_questions':[], 'scope_grants':[]}
    events = [{'type':'item.completed','item':{'type':'agent_message','text':json.dumps(payload)}},
              {'type':'turn.completed'}]
elif provider == 'codex':
    events = [ {'type':'thread.started', 'thread_id':'synthetic', 'future':None},
              {'type':'item.completed','item':{'type':'agent_message','text':json.dumps({'result':'ñ'})}},
              {'type':'turn.failed','error':{'message':'synthetic quota'}} if mode == 'error'
              else {'type':'turn.completed','usage':{'input_tokens':0}} ]
else:
    events = [ {'type':'system','subtype':'init','session_id':'synthetic','model':None},
              {'type':'stream_event','event':{'delta':{'text':'ñ'}}},
              {'type':'future.event','opaque':{'a':None}},
              {'type':'result','subtype':'error_during_execution' if mode=='error' else 'success',
               'is_error':mode=='error', 'result': 'not structured' if mode=='bad_payload' else
                  json.dumps({'result':'ñ'}), 'usage':None,'duration_ms':0} ]
if mode == 'double_terminal':
    events.append(events[-1])
for event in events:
    raw = (json.dumps(event,ensure_ascii=False)+'\n').encode()
    # Force UTF-8 and JSON splits.
    for byte in raw:
        os.write(1,bytes([byte]))
        if mode == 'slow':
            time.sleep(.001)
os.write(2,b'synthetic stderr\xff\n')
sys.exit(7 if mode == 'exit_error' else 0)
