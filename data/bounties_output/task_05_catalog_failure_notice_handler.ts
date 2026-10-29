// Fix: Keep catalog failure notice visible during proposal edits
export function reconcileCatalogErrorState(hasCatalogError: boolean, isEditing: boolean): boolean {
  // Never suppress catalog failure notice when user enters edit mode
  return hasCatalogError;
}
