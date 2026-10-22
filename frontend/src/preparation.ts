export function pendingPreparationStep(steps: { number: number; status: string }[]): number | undefined {
  return steps.find(step => step.status !== 'DONE')?.number ?? steps.at(-1)?.number;
}
/** P010-T002 (D142): what each packaged recipe prepares, by its frozen `project_recipe`. */
export function recipeLabel(recipe: string | null | undefined): string {
  return ({ 'django-recipe-1': 'Django', 'typescript-web-recipe-1': 'TypeScript web' } as Record<string, string>)[recipe ?? ''] ?? 'el proyecto';
}
export function recipeModes(recipe: string | null | undefined): { offline: string; network: string; hint: string } {
  return recipe === 'typescript-web-recipe-1'
    ? { offline: 'Offline: usar solo la caché npm declarada por el operador',
        network: 'Red: descargar del registro npm el lock fijado',
        hint: 'node_modules queda dentro del hijo; la caché npm es la del operador y con red también se escribe en ella. Un fallo detiene la preparación y conserva sus bytes; no se repite ningún comando automáticamente.' }
    : { offline: 'Offline: usar wheels locales y caché del hijo',
        network: 'Red: descargar wheels fijados de PyPI',
        hint: 'La caché y el entorno permanecen dentro del hijo. Un fallo detiene la preparación y conserva sus bytes; no se repite ningún comando automáticamente.' };
}
export function preparationStatus(status: string, recipe?: string | null): string {
  const label = recipeLabel(recipe);
  return ({ QUEUED: 'En cola', ACTIVE: `Preparando ${label}`, FAILED: 'Detenida por un fallo',
    RECOVERY_REQUIRED: 'Requiere conciliación', CANCELLED: 'Cancelada', COMPLETED: recipe ? `${label} preparado` : 'Proyecto preparado' } as Record<string, string>)[status] ?? status;
}
