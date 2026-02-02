import React, { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { Role } from "../models/user";
import { useAuth } from "./Authentication/AuthContext";
import { AppModel } from "../models/app";
import {
    fetchCatalogApplications,
    fetchInstalledApplications,
    claimApplicationAsDataController,
    assignDpoToApplication,
    updateCatalogApplications,
} from "../services/ApplicationService";
import { useHome } from "./HomeContext";
import { PrivacyNotice } from "../models/privacy_notice";
import { handleFetchPrivacyNotice } from "../services/PrivacyNoticeService";
//tutti i parametri del contesto che possono essere comodi e usati in tanti componenti diversi
type AppsContextValue = {

    apps: AppModel[] | undefined; //per data subject sono le installed apps, per data controller / dpo sono le catalog apps
    managedApps: AppModel[]; //sottoinsieme derivato da `apps` (per DS coincide con `apps`)
    loadingApps: boolean;
    updatingApps: boolean;
    errorApps: string | undefined;
    errorUpdatingApps: string | undefined;
    PrivacyNoticeByAppUUID: Record<string, PrivacyNotice | null | undefined>

    loadPrivacyNotice: (appUUID: string, force: boolean) => Promise<PrivacyNotice | null | undefined>
    claimManagedApplication: (appUUID: string) => Promise<boolean | undefined>
    assignDpoToManagedApplication: (appUUID: string, dpoUUID: string) => Promise<boolean | undefined>
    syncApps: () => Promise<void>;

};

const AppsContext = React.createContext<AppsContextValue | undefined>(undefined);

//dove mettere tutte le funzioni ed è quello da importare in react che wrappa tutto
export function AppsProvider({ children }: { children: React.ReactNode }) {

    const { user, loading } = useAuth();
    const { current_home_uuid, loadingHomes } = useHome();

    const [PrivacyNoticeByAppUUID, setPrivacyNoticeByAppUUID] = useState<Record<string, PrivacyNotice | null | undefined>>({});

    const [apps, setApps] = useState<AppModel[] | undefined>(undefined);
    const [loadingApps, setLoadingApps] = useState(true);
    const [updatingApps, setUpdatingApps] = useState(false);
    const [errorApps, setErrorApps] = useState<string | undefined>(undefined);
    const [errorUpdatingApps, setErrorUpdatingApps] = useState<string | undefined>(undefined);


    const managedApps = useMemo<AppModel[]>(() => {

        if (!user) return [];
        const list = apps ?? [];

        if (user.role === Role.DataSubject) return list;

        if (user.role === Role.DatController) {
            return list.filter(
                (app) =>
                    app.data_controllers?.some((dc) => dc.uuid === user.uuid) ??
                    false,
            );
        }

        if (user.role === Role.DPO) {
            return list.filter((app) => app.dpo?.uuid === user.uuid);
        }

        return [];
    }, [apps, user?.role, user?.uuid]);


    //sync local database if information on the backend changes
    useEffect(() => {

        if (loading) return;
        if (!user) {
            setApps(undefined);
            setLoadingApps(false);
            setUpdatingApps(false);
            setErrorApps(undefined);
            setErrorUpdatingApps(undefined);
            setPrivacyNoticeByAppUUID({});
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

    const claimManagedApplication = useCallback(async (appUUID: string): Promise<boolean | undefined> => {

        if (!user) return undefined;
        if (user.role !== Role.DatController) return undefined;

        const created = await claimApplicationAsDataController(appUUID);
        await loadApps();
        return created;
    },
        [loadApps, user],
    );

    const assignDpoToManagedApplication = useCallback(async (appUUID: string, dpoUUID: string): Promise<boolean | undefined> => {

        if (!user) return undefined;
        if (user.role !== Role.DatController) return undefined;

        const created = await assignDpoToApplication(appUUID, dpoUUID);
        await loadApps();
        return created;
    },
        [loadApps, user],
    );


    const loadPrivacyNotice = useCallback(async (appUUID: string, force: boolean): Promise<PrivacyNotice | null | undefined> => {
        if (!user) return undefined;

        //ritorna undefined se il data controller non la gestisce
        if (user.role !== Role.DataSubject) {
            const isManaged = managedApps.some((app) => app.uuid === appUUID);
            if (!isManaged) {
                return undefined;
            }
        }

        if (force == false) {
            const cached = PrivacyNoticeByAppUUID[appUUID];
            if (cached !== undefined) {
                return cached;
            }
        }

        //se non presente in cache la recuperiamo
        try {
            const res = await handleFetchPrivacyNotice(appUUID, user.role);
            setPrivacyNoticeByAppUUID(prev => ({ ...prev, [appUUID]: res })); //può essere a questo punto o un valore o un null
            return res;
        }
        catch (err) {
            //vedere cosa fare dell'errore
            return undefined //rimesso a undefined perchè non è stato caricato correttamente
        }
    },
        [user, managedApps, PrivacyNoticeByAppUUID],
    );




    //per ottimizzare il caricamento riguardare meglio
    const value = useMemo<AppsContextValue>(
        () => ({
            apps,
            managedApps,
            PrivacyNoticeByAppUUID,
            loadingApps,
            updatingApps,
            errorApps,
            errorUpdatingApps,
            syncApps,
            claimManagedApplication,
            assignDpoToManagedApplication,
            loadPrivacyNotice,
        }),
        [
            apps,
            managedApps,
            PrivacyNoticeByAppUUID,
            loadingApps,
            updatingApps,
            errorApps,
            errorUpdatingApps,
            syncApps,
            claimManagedApplication,
            assignDpoToManagedApplication,
            loadPrivacyNotice,
        ],
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
