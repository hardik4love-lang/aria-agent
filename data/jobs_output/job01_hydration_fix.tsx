import React, { useState, useEffect, ReactNode } from "react";

interface ClientOnlyProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export function useIsMounted(): boolean {
  const [mounted, setMounted] = useState<boolean>(false);
  useEffect(() => {
    setMounted(true);
  }, []);
  return mounted;
}

export function ClientOnly({ children, fallback = null }: ClientOnlyProps) {
  const isMounted = useIsMounted();
  if (!isMounted) return <>{fallback}</>;
  return <>{children}</>;
}

export function useSafeLocalStorage<T>(key: string, initialValue: T): [T, (val: T) => void] {
  const [storedValue, setStoredValue] = useState<T>(initialValue);
  useEffect(() => {
    try {
      const item = window.localStorage.getItem(key);
      if (item) setStoredValue(JSON.parse(item));
    } catch (err) {
      console.warn(`[SafeLocalStorage] Read error for ${key}:`, err);
    }
  }, [key]);

  const setValue = (val: T) => {
    try {
      setStoredValue(val);
      window.localStorage.setItem(key, JSON.stringify(val));
    } catch (err) {
      console.warn(`[SafeLocalStorage] Write error for ${key}:`, err);
    }
  };

  return [storedValue, setValue];
}
