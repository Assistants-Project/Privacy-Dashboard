import React, { useContext, useEffect, useMemo, useState } from "react";
import { UserModel, Role } from "../models/user";
import authentication from "../API/User/authenticationAPI";

//tutti i parametri del contesto che possono essere comodi e usati in tanti componenti diversi
type AuthContextValue = {
  user: UserModel | undefined;
  loading: boolean;
  loginEventId: number;
  isDataSubject: boolean;
  isDataController: boolean;
  isDpo: boolean;
  isManagerRole: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (
    email: string,
    firstname: string,
    lastname: string,
    password: string,
    role: Role,
  ) => Promise<void>;
  updateProfile: (payload: { current_password: string; email?: string; new_password?: string; }) => Promise<void>;
  logout: () => Promise<void>;
  deleteUser: () => Promise<void>;
};

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

//dove mettere tutte le funzioni ed è quello da importare in react che wrappa tutto
export function AuthProvider({ children }: { children: React.ReactNode }) {

  const [user, setUser] = useState<UserModel | undefined>(undefined);
  const [loginEventId, setLoginEventId] = useState(0);

  const [loading, setLoading] = useState(true);

  //redirect user to the home page if a session is established
  useEffect(() => {

    const checkAuth = async () => {

      try {
        const u = await authentication.getUserInfo();
        setUser(
          new UserModel(u.uuid, u.email, u.firstname, u.lastname, u.role),
        );
        console.log("User is authenticated, redirecting to home page.");
      } catch { 
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [user?.uuid]);

  const deleteUser = async() => {
    await authentication.delete_current();
    setUser(undefined)
  } 


  const login = async (email: string, password: string) => {
    const u = await authentication.login(email, password);
    setUser(new UserModel(u.uuid,u.email, u.firstname, u.lastname, u.role));
    //id incrementato solo durante login esplicito, non durante checkAuth su reload
    setLoginEventId((prev) => prev + 1);
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

  const updateProfile = async (payload: { current_password: string; email?: string; new_password?: string; }) => {
    const u = await authentication.updateCurrentUserProfile(payload);
    setUser(new UserModel(u.uuid, u.email, u.firstname, u.lastname, u.role));
  };

  const isDataSubject = user?.role === Role.DataSubject;
  const isDataController = user?.role === Role.DataController;
  const isDpo = user?.role === Role.DPO;
  const isManagerRole = isDataController || isDpo;

  //per ottimizzare il caricamento riguardare meglio
  const value = useMemo<AuthContextValue>(
    () => ({ user, loading, loginEventId, isDataSubject, isDataController, isDpo, isManagerRole, login, register, updateProfile, logout, deleteUser }),
    [user, loading, loginEventId, isDataSubject, isDataController, isDpo, isManagerRole],
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
