import React, { useContext, useEffect, useMemo, useState } from "react";
import { User, Role } from '../../models/user';
import authentication from "../API/User/authentication";
import { fetchHomes } from "../services/HomesService"
import { HomeModel } from "../../models/home";

//tutti i parametri del contesto che possono essere comodi e usati in tanti componenti diversi
type AuthContextValue = {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  registration: (
    newUsername: string,
    name: string,
    surname: string,
    newPassword: string,
    role: string,
  ) => void;
  logout: () => Promise<void>;
  setHome: (user: User, current_home: HomeModel) => void
};

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

//dove mettere tutte le funzioni ed è quello da importare in react che wrappa tutto
export function AuthProvider({ children }: { children: React.ReactNode }) {

  const [user, setUser] = useState<User | null>(null);

  const setHome = (user: User, new_current_home: HomeModel) => {
    setUser(
        new User(user.email, user.firstname, user.lastname, user.role, user.homes, new_current_home),
    );
  }

  //redirect user to the home page if a session is established
  useEffect(() => {

    const checkAuth = async () => {

      try {
        const u = await authentication.getUserInfo();
        const homes =
          u.role === Role.DataSubject ? await fetchHomes() : undefined;
        setUser(
          new User(u.email, u.firstname, u.lastname, u.role, homes, homes?.[0]),
        );
        console.log("User is authenticated, redirecting to home page.");
      } catch { }
    };

    checkAuth();
  }, []);


  const login = async (email: string, password: string) => {
    try {
      const u = await authentication.login(email, password);
      //prendo le case solo se utente è data subject
      const homes = u.role === Role.DataSubject ? await fetchHomes() : undefined;
      setUser(new User(u.email, u.firstname, u.lastname, u.role, homes, homes?.[0]));
    } catch (err) {
        const msg =
                    err instanceof Error
                        ? err.message
                        : typeof err === "string"
                            ? err
                            : (err as any)?.error ||
                              (err as any)?.message ||
                              "An error occurred";
      throw msg;
    }
  };

  const registration = (
    newUsername: string,
    name: string,
    surname: string,
    newPassword: string,
    role: string,
  ) => {
    // FAKE REGISTRATION
    console.debug("Registrazione utente", {
      newUsername,
      name,
      surname,
      role,
      newPassword,
    });
  };

  const logout = async () => {
    try {
      await authentication.logOut();
    } catch (err) {
      console.warn("Logout fallito", err);
    } finally {
      setUser(null);
    }
  };

  //per ottimizzare il caricamento riguardare meglio
  const value = useMemo<AuthContextValue>(
    () => ({ user, login, logout, registration, setHome }),
    [user],
  );

  return <AuthContext.Provider value={ value }>{children}</AuthContext.Provider>;
}

//funzione hook che è possibile chiamare per ottenere i valori del contesto 
//la funzione deve essere chiamata dentro un componente wrappato dal contesto AuthProvider
export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useUser fuori da UserProvider');
  return value;
}
