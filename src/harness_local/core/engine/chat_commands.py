"""Sintaxis cerrada: una barra inicial nunca se envía implícitamente a un modelo."""
COMMANDS = ('estado', 'tests', 'siguiente', 'lote', 'check', 'cerrar', 'exportar', 'abrir-fase', 'tarea')


def parse(text):
    text = text.strip()
    if not text.startswith('/'):
        return None
    parts = text.split(maxsplit=1)
    name = parts[0][1:]
    argument = parts[1].strip() if len(parts) == 2 else ''
    if name not in COMMANDS or (name == 'tarea') != bool(argument):
        raise ValueError('Comando inválido. Usa /' + ', /'.join(COMMANDS[:-1]) + ' o /tarea <texto>.')
    if len(argument) > 4000:
        raise ValueError('/tarea admite hasta 4000 caracteres')
    return {'name': name, 'argument': argument}


def proposal(argument):
    return {'answer': 'Propuesta creada sin agente. Revisa el objetivo antes de confirmar la tarea.',
            'references': [], 'proposals': [{'title': argument[:200], 'objective': argument, 'scope': '',
                'acceptance_criteria': [argument], 'validation': [],
                'rationale': 'Petición explícita /tarea; el planificador fijará el contrato bajo la política del proyecto.'}]}
