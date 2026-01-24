import React, { useContext, useEffect, useMemo, useState } from "react";
import { User, Role } from '../../../models/user';
import authentication from "../../API/User/authenticationAPI";
import { fetchHomes } from "../../services/HomesService"
import { HomeModel } from "../../../models/home";

//tutti i parametri del contesto che possono essere comodi e usati in tanti componenti diversi
type AuthContextValue = {
  user: User | undefined;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (
    email: string,
    firstname: string,
    lastname: string,
    password: string,
    role: Role,
  ) => Promise<void>;
  logout: () => Promise<void>;
  setHome: (user: User, current_home: HomeModel) => void
  delete_user: () => Promise<void>;
};

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

//dove mettere tutte le funzioni ed è quello da importare in react che wrappa tutto
export function AuthProvider({ children }: { children: React.ReactNode }) {

  const [user, setUser] = useState<User | undefined>(undefined);

  const [loading, setLoading] = useState(true);

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
      } catch { 
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const delete_user = async() => {
    await authentication.delete_current();
    setUser(undefined)
  } 


  const login = async (email: string, password: string) => {
    const u = await authentication.login(email, password);
    //prendo le case solo se utente è data subject
    const homes = u.role === Role.DataSubject ? await fetchHomes() : undefined;
    setUser(new User(u.email, u.firstname, u.lastname, u.role, homes, homes?.[0]));
  };


  const register = async (
    email: string,
    firstname: string,
    lastname: string,
    password: string,
    role: Role,
  ) => {

    console.debug("Registrazione utente", {
      email,
      firstname,
      lastname,
      role,
      password,
    });

    await authentication.register(email,firstname,lastname,password,role)

  };

  const logout = async () => {
    try {
      await authentication.logOut();
    } catch (err) {
      console.warn("Logout fallito", err);
    } finally {
      setUser(undefined);
    }
  };

  //per ottimizzare il caricamento riguardare meglio
  const value = useMemo<AuthContextValue>(
    () => ({ user, loading, login, logout, register, setHome, delete_user }),
    [user, loading],
  );

  return <AuthContext.Provider value={ value }>{children}</AuthContext.Provider>;
}

//funzione hook che è possibile chiamare per ottenere i valori del contesto 
//la funzione deve essere chiamata dentro un componente wrappato dal contesto AuthProvider
export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth fuori da AuthProvider');
  return value;
}
