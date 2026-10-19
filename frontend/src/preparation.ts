export function pendingPreparationStep(steps: { number: number; status: string }[]): number | undefined {
  return steps.find(step => step.status !== 'DONE')?.number ?? steps.at(-1)?.number;
}
export function preparationStatus(status: string): string {
  return ({ QUEUED: 'En cola', ACTIVE: 'Preparando Django', FAILED: 'Detenida por un fallo',
    RECOVERY_REQUIRED: 'Requiere conciliación', CANCELLED: 'Cancelada', COMPLETED: 'Django preparado' } as Record<string, string>)[status] ?? status;
}
