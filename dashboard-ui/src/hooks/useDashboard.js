import { useState, useEffect, useCallback } from 'react';

const API_BASE = '/api/dashboard';

export function useDashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSummary = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/summary`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      setSummary(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  return { summary, loading, error, refetch: fetchSummary };
}

export function useEmployeeSessions(email) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!email) {
      setData(null);
      return;
    }

    let cancelled = false;
    const fetchSessions = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/employee/${encodeURIComponent(email)}/sessions`);
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        const result = await res.json();
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchSessions();
    return () => { cancelled = true; };
  }, [email]);

  return { data, loading, error };
}
