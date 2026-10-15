"""H4.2: ejecución del bootstrap confirmado; no proveedores, web, SQLite ni stack en el núcleo.

D088: la plantilla v1 (`project-foundation`) está retirada; la vista previa sale de la definición v2."""
from dataclasses import replace


def execute(context, history, saved, git, journal):
    journal.checkpoint(history, 'bootstrap')
    result = git.execute_bootstrap(context, saved['preview'], saved['intent'])
    return replace(history, status='completed', stop=None), result
