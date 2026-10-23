"""P011-T013: compares the erDiagram blocks of docs/DDBB-DIAGRAM.md with the SQLAlchemy metadata.

Usage from the repository root:
    UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P011-T013_er_parity.py docs/DDBB-DIAGRAM.md
Checks tables, columns, types, PK/FK/UK flags, nullability, drawn relations and listed uniqueness. Read-only.
"""
import re
import sys
from pathlib import Path

from sqlalchemy import Boolean, Float, Integer, JSON, LargeBinary, String, Text

from harness_local.storage.models import Base

TYPES = {'string': String, 'text': Text, 'integer': Integer, 'boolean': Boolean, 'json': JSON, 'float': Float,
         'blob': LargeBinary, 'binary': LargeBinary, 'bytes': LargeBinary}
document = Path(sys.argv[1]).read_text()
blocks = re.findall(r'```mermaid\nerDiagram\n(.*?)```', document, re.S)
entities: dict[str, list[dict]] = {}
relations = set()
for block in blocks:
    for name, body in re.findall(r'^\s*(\w+) \{\n(.*?)^\s*\}', block, re.S | re.M):
        columns = {}
        for line in body.strip().splitlines():
            match = re.match(r'\s*(\w+) (\w+)(?: ((?:PK|FK|UK)(?:, ?(?:PK|FK|UK))*))?(?: "(.*)")?\s*$', line)
            if not match:
                print('UNPARSED', name, line)
                continue
            kind, column, keys, comment = match.groups()
            columns[column] = {'type': kind, 'keys': set(re.findall(r'PK|FK|UK', keys or '')), 'comment': comment or ''}
        entities.setdefault(name, []).append(columns)
    for left, right, label in re.findall(r'^\s*(\w+) \S+ (\w+) : "?([^"\n]*)"?', block, re.M):
        relations.add(frozenset((left, right)))

tables = Base.metadata.tables
problems = []
documented = set(entities)
missing = sorted(set(tables) - documented)
extra = sorted(documented - set(tables))
problems += [f'table missing from diagram: {t}' for t in missing] + [f'unknown table in diagram: {t}' for t in extra]
column_total = 0
for name in sorted(documented & set(tables)):
    table = tables[name]
    full = max(entities[name], key=len)
    column_total += len(table.columns)
    names = set(table.columns.keys())
    if set(full) != names:
        problems.append(f'{name}: columns differ; missing {sorted(names - set(full))}, extra {sorted(set(full) - names)}')
    for appearance in entities[name]:
        for column, info in appearance.items():
            if column not in table.columns:
                problems.append(f'{name}.{column}: not in metadata')
                continue
            meta = table.columns[column]
            expected = TYPES.get(info['type'])
            if expected is None or not isinstance(meta.type, expected) or (
                    info['type'] == 'string' and isinstance(meta.type, Text)):
                problems.append(f'{name}.{column}: type {info["type"]} vs {type(meta.type).__name__}')
            if ('PK' in info['keys']) != bool(meta.primary_key):
                problems.append(f'{name}.{column}: PK flag mismatch')
            if appearance is full:  # abbreviated references only show related columns
                if ('FK' in info['keys']) != bool(meta.foreign_keys):
                    problems.append(f'{name}.{column}: FK flag mismatch')
                single_index = any(i.unique and [c.name for c in i.columns] == [column] and i.dialect_options['sqlite'].get('where') is None for i in table.indexes)
                if ('UK' in info['keys']) != bool(meta.unique or single_index):
                    problems.append(f'{name}.{column}: UK flag mismatch')
                nullable = info['comment'].startswith('null')
                if not meta.primary_key and nullable != bool(meta.nullable):
                    problems.append(f'{name}.{column}: nullable {meta.nullable} vs diagram {nullable}')
    for fk in table.foreign_keys:
        target = fk.column.table.name
        if target != name and frozenset((name, target)) not in relations:
            problems.append(f'{name}.{fk.parent.name}: relation to {target} not drawn')
# Composite uniqueness and partial unique indexes must be named in the prose.
for table in tables.values():
    for constraint in table.constraints:
        if type(constraint).__name__ == 'UniqueConstraint' and len(constraint.columns) > 1:
            cols = ', '.join(c.name for c in constraint.columns)
            if f'({cols})' not in document and (constraint.name or '@@') not in document:
                problems.append(f'composite unique not listed: {table.name} ({cols})')
    for index in table.indexes:
        if index.unique and index.name not in document:
            problems.append(f'unique index not listed: {index.name} on {table.name}')
print(f'{len(tables)} tables, {column_total} columns, {len(blocks)} ER blocks, {len(relations)} relations drawn')
print('\n'.join(problems) or 'no problems')
