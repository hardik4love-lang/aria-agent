'use client';
import React, { useState, useEffect } from 'react';

export function useIsMounted(): boolean {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);
  return mounted;
}

export function ClientOnly({ children, fallback = null }: { children: React.ReactNode; fallback?: React.ReactNode }) {
  const isMounted = useIsMounted();
  if (!isMounted) return <React.Fragment>{fallback}</React.Fragment>;
  return <React.Fragment>{children}</React.Fragment>;
}

// Patched ThemeSwitcher safely accessing localStorage without hydration error:
export function PatchedThemeSwitcher() {
  const isMounted = useIsMounted();
  const [value, setValue] = useState('default');

  useEffect(() => {
    const saved = localStorage.getItem('app-pref') || 'default';
    setValue(saved);
  }, []);

  if (!isMounted) return <div className="h-8 w-24 bg-gray-200 animate-pulse rounded" />;
  return <div className="p-2 border rounded font-medium">Loaded: {value}</div>;
}
