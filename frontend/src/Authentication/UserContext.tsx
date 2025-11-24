import React, { useContext, useState } from 'react';
import { User } from '../../models/user';

type UserCtx = {
  user: User | null;
  setUser: (u: User | null) => void;
};

const UserContext = React.createContext<UserCtx | undefined>(undefined);

export function useUser() {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error('useUser fuori da UserProvider');
  return ctx;
}

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  return <UserContext.Provider value={{ user, setUser }}>{children}</UserContext.Provider>;
}
