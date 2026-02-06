import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { useMe } from '@/hooks/useAuth';

interface User {
  id: string;
  email: string;
  full_name?: string;
  business_name?: string;
  user_type: 'user' | 'owner';
  phone_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const { data: user, isLoading } = useMe();

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  }, [user]);

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_type');
    setIsAuthenticated(false);
    window.location.href = '/';
  };

  return (
    <AuthContext.Provider
      value={{
        user: user || null,
        isLoading,
        isAuthenticated,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
