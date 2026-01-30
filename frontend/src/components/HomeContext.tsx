import React, { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { Role } from "../models/user";
import { fetchHomes, updateHomesService } from "../services/HomesService"
import { HomeModel } from "../models/home";
import { useAuth } from "./Authentication/AuthContext";

//tutti i parametri del contesto che possono essere comodi e usati in tanti componenti diversi
type HomeContextValue = {
    current_home_uuid: string | undefined;
    loadingHomes: boolean;
    updatingHomes: boolean;
    errorHomes: string | undefined;
    errorupdatingHomes: string | undefined
    homes: HomeModel[] | undefined;
    updateCurrentHomeUUID: (current_home: string) => void;
    syncHomes: () => Promise<void>;

};

const HomeContext = React.createContext<HomeContextValue | undefined>(undefined);

//dove mettere tutte le funzioni ed è quello da importare in react che wrappa tutto
export function HomeProvider({ children }: { children: React.ReactNode }) {

    const { user, loading } = useAuth();

    const [current_home_uuid, setCurrent_home_uuid] = useState<string | undefined>(undefined);
    const [homes, setHomes] = useState<HomeModel[] | undefined>(undefined);

    const [loadingHomes, setLoadingHomes] = useState(true);
    const [updatingHomes, setUpdatingHomes] = useState(false);
    const [errorHomes, setErrorHomes] = useState<string | undefined>(undefined);
    const [errorupdatingHomes, setErrorUpdatingHomes] = useState<string | undefined>(undefined);


    const updateCurrentHomeUUID = useCallback((uuid: string) => {
        // valutare se controllare che esiste
        setCurrent_home_uuid(uuid);
    }, []);

    //sync local database if information on the backend changes
    useEffect(() => {

        if (loading) return;

        if (updatingHomes) return;

        if (user?.role != Role.DataSubject) {
            setCurrent_home_uuid(undefined);
            setHomes(undefined);
            setLoadingHomes(false);
            setUpdatingHomes(false);
            setErrorHomes(undefined);
            setErrorUpdatingHomes(undefined);
            return
        }


        loadHomes();
    }, [loading, updatingHomes, user?.uuid]);

    const loadHomes = async () => {

        setLoadingHomes(true);
        setErrorHomes(undefined);

        try {

            const homes = await fetchHomes();
            setHomes(homes)

            //add if current home still exist we don't change it
            let exist = homes?.some((home) => home.uuid === current_home_uuid) ?? false;
            if (!exist) {
                setCurrent_home_uuid(homes?.[0].uuid);
            }
           
        } catch (err) {
            setErrorHomes(err instanceof Error ? err.message : "Errore inatteso")
        } finally {
            setLoadingHomes(false);
        }
    };

    const syncHomes = useCallback(async () => {

        setUpdatingHomes(true);
        setErrorUpdatingHomes(undefined);

        try {
            await updateHomesService();
        } catch (err) {
            setErrorUpdatingHomes(err instanceof Error ? err.message : "Errore inatteso")
        } finally {
            setUpdatingHomes(false);
        }
    }, []);


    //per ottimizzare il caricamento riguardare meglio
    const value = useMemo<HomeContextValue>(
        () => ({current_home_uuid,loadingHomes,updatingHomes,errorHomes,errorupdatingHomes,homes,updateCurrentHomeUUID,syncHomes}),
        [current_home_uuid, loadingHomes, updatingHomes, errorHomes, errorupdatingHomes, homes, updateCurrentHomeUUID, syncHomes],
    );

    return <HomeContext.Provider value={value}>{children}</HomeContext.Provider>;
}

//funzione hook che è possibile chiamare per ottenere i valori del contesto 
//la funzione deve essere chiamata dentro un componente wrappato dal contesto AuthProvider
export function useHome(): HomeContextValue {
    const value = useContext(HomeContext);
    if (!value) throw new Error("useHome fuori da HomeProvider");
    return value;
}
