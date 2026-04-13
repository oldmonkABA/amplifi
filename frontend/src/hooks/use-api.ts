"use client";

import { useState, useEffect, useCallback } from "react";
import { getToken } from "@/lib/api";

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useApi<T>(
  fetcher: (token: string) => Promise<T>,
  deps: unknown[] = [],
): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const refetch = useCallback(() => setRefreshKey((k) => k + 1), []);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetcher(token)
      .then((result) => {
        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [refreshKey, ...deps]);

  return { data, loading, error, refetch };
}

export function useMutation<TInput, TOutput>(
  mutator: (token: string, input: TInput) => Promise<TOutput>,
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(
    async (input: TInput): Promise<TOutput> => {
      const token = getToken();
      if (!token) throw new Error("Not authenticated");
      setLoading(true);
      setError(null);
      try {
        const result = await mutator(token, input);
        return result;
      } catch (err: any) {
        setError(err.message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [mutator],
  );

  return { execute, loading, error };
}
