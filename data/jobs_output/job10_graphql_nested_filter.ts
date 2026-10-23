export type FilterOperator<T> = {
  equals?: T;
  not?: T;
  in?: T[];
  notIn?: T[];
  lt?: T;
  lte?: T;
  gt?: T;
  gte?: T;
  contains?: string;
};

export type CompoundFilter<T> = {
  [K in keyof T]?: FilterOperator<T[K]>;
} & {
  AND?: CompoundFilter<T>[];
  OR?: CompoundFilter<T>[];
  NOT?: CompoundFilter<T>[];
};

export function compileWhereClause<T>(filter: CompoundFilter<T>): Record<string, any> {
  const where: Record<string, any> = {};
  for (const [key, value] of Object.entries(filter)) {
    if (key === "AND" || key === "OR" || key === "NOT") {
      where[key] = (value as CompoundFilter<T>[]).map(compileWhereClause);
    } else {
      where[key] = value;
    }
  }
  return where;
}
