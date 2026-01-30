import React, { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { Role } from "../models/user";
import { useAuth } from "./Authentication/AuthContext";
import { AppModel } from "../models/app";
import {
    fetchCatalogApplications,
    fetchInstalledApplications,
    updateCatalogApplications,
} from "../services/ApplicationService";
import { useHome } from "./HomeContext";
//tutti i parametri del contesto che possono essere comodi e usati in tanti componenti diversi
type AppsContextValue = {

    apps: AppModel[] | undefined;
    loadingApps: boolean;
    updatingApps: boolean;
    errorApps: string | undefined;
    errorUpdatingApps: string | undefined;
    
    syncApps: () => Promise<void>;

};

const AppsContext = React.createContext<AppsContextValue | undefined>(undefined);

//dove mettere tutte le funzioni ed è quello da importare in react che wrappa tutto
export function AppsProvider({ children }: { children: React.ReactNode }) {

    const { user, loading } = useAuth();
    const { current_home_uuid, loadingHomes } = useHome();
    

    const [apps, setApps] = useState<AppModel[] | undefined>(undefined);
    const [loadingApps, setLoadingApps] = useState(true);
    const [updatingApps, setUpdatingApps] = useState(false);
    const [errorApps, setErrorApps] = useState<string | undefined>(undefined);
    const [errorUpdatingApps, setErrorUpdatingApps] = useState<string | undefined>(undefined);


    //sync local database if information on the backend changes
    useEffect(() => {

        if (loading) return;
        if (!user) {
            setApps(undefined);
            setLoadingApps(false);
            setUpdatingApps(false);
            setErrorApps(undefined);
            setErrorUpdatingApps(undefined);
            return;
        }

        if (updatingApps) return;
        if (user.role === Role.DataSubject && loadingHomes) return;

        loadApps();
    }, [loading, updatingApps, user?.uuid, current_home_uuid, loadingHomes]);

    const loadApps = useCallback(async () => {

        setLoadingApps(true);
        setErrorApps(undefined);

        try {

            let res: AppModel[] | undefined = [];

            if (user?.role === Role.DataSubject) {
                if (!current_home_uuid) {
                    res = [];
                } else {
                    res = await fetchInstalledApplications(current_home_uuid);
                }
            } else {
                res = await fetchCatalogApplications();
            }


            if (!res) {
                setApps([]);
                setErrorApps("Impossibile caricare le applicazioni.");
                setLoadingApps(false);
                return;
            }

            setApps(res);
            setLoadingApps(false);
        }
        catch (err) {
            setLoadingApps(false)
            setErrorApps(err instanceof Error ? err.message : "Errore inatteso")
        }
    }, [current_home_uuid, user?.role]);

    const syncApps = useCallback(async () => {
        if (!user) return;

        setUpdatingApps(true);
        setErrorUpdatingApps(undefined);

        try {
            await updateCatalogApplications();
        } catch (err) {
            setErrorUpdatingApps(err instanceof Error ? err.message : "Errore inatteso")
        } finally {
            setUpdatingApps(false);
        }
    }, [user]);


    //per ottimizzare il caricamento riguardare meglio
    const value = useMemo<AppsContextValue>(
        () => ({ apps, loadingApps, updatingApps, errorApps, errorUpdatingApps, syncApps }),
        [apps, loadingApps, updatingApps, errorApps, errorUpdatingApps, syncApps],
    );

    return <AppsContext.Provider value={value}>{children}</AppsContext.Provider>;
}

//funzione hook che è possibile chiamare per ottenere i valori del contesto 
//la funzione deve essere chiamata dentro un componente wrappato dal contesto AuthProvider
export function useApp(): AppsContextValue {
    const value = useContext(AppsContext);
    if (!value) throw new Error("useApp fuori da AppsProvider");
    return value;
}
