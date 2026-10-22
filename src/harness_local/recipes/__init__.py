"""Packaged deterministic recipes; never repository or browser supplied scripts."""
from importlib import import_module

# P010-T002 (D142): configuration name → packaged module and the profile its composition must name.
# `django.py` stays byte-identical: its text is part of the fingerprint bound to issued receipts.
RECIPES = {'django': ('harness_local.recipes.django', 'python-django-recipe'),
           'typescript-web': ('harness_local.recipes.typescript_web', 'typescript-web')}


def module(name):
    return import_module(RECIPES[name][0])


def by_version(version):
    """Configuration name and module of a frozen `project_recipe`, or None for an unknown version."""
    for name in RECIPES:
        recipe = module(name)
        if recipe.VERSION == version:
            return name, recipe
    return None
