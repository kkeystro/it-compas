import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { AuthUser } from '../types/auth';
import { getMe } from '../api/auth';

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  loginUser: (user: AuthUser) => void;
  logoutUser: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const AUTH_KEY = 'authToken';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Restore session from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(AUTH_KEY);
    if (stored) {
      try {
        const parsed: AuthUser = JSON.parse(stored);
        // Verify token is still valid
        getMe(parsed.token)
          .then(() => {
            setUser(parsed);
          })
          .catch(() => {
            // Token expired or invalid
            localStorage.removeItem(AUTH_KEY);
          })
          .finally(() => setLoading(false));
      } catch {
        localStorage.removeItem(AUTH_KEY);
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  const loginUser = (userData: AuthUser) => {
    localStorage.setItem(AUTH_KEY, JSON.stringify(userData));
    setUser(userData);
  };

  const logoutUser = () => {
    localStorage.removeItem(AUTH_KEY);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token: user?.token ?? null,
        loginUser,
        logoutUser,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
