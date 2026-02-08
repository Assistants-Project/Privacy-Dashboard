import React, {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { Role } from "../models/user";
import { useAuth } from "./AuthContext";
import { AppModel, DocumentStatus } from "../models/app";
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
import { handleGetPrivacyImpactAssessment } from "../services/PrivacyImpactAssessmentService";
import { PIA } from "../models/PIA";
import { Questionnaire } from "../models/question";
import { handleGetQuestionnaireByApplication } from "../services/QuestionnaireService";
//tutti i parametri del contesto che possono essere comodi e usati in tanti componenti diversi
type AppsContextValue = {
  apps: AppModel[] | undefined; //per data subject sono le installed apps, per data controller / dpo sono le catalog apps
  selectedAppUUID: string | undefined; //è l'uuid dell'app selezionata dal sistema Catalog/InstalledApp/PIA/PN
  selectedApp: AppModel | undefined; //l'app selezionata corrente dal sistema Catalog/InstalledApp/PIA/PN
  managedApps: AppModel[]; //sottoinsieme derivato da apps (per DS coincide con apps)
  loadingApps: boolean; //indica se è in corso un fetch delle apps dal backend
  errorApps: string | undefined; //indica se c'è stato un errore durante il fetch delle apps dal backend
  updatingApps: boolean; //indica se è in corso un update delle apps nel backend (attraverso un refresh)
  errorUpdatingApps: string | undefined; //indica se c'è stato un errore durante il refresh del backend
  PrivacyNoticeByAppUUID: Record<string, PrivacyNotice | null | undefined>; //record cache dei PN
  PIAByAppUUID: Record<string, PIA | null | undefined>; //record cache dei PIA
  QuestionnaireByAppUUID: Record<string, Questionnaire | null | undefined>; //record cache dei Questionnaire

  reloadApps: () => Promise<void>;

  //espone modo per cambiare app selezionata
  setSelectedAppUUID: (uuid: string | undefined) => void;

  //ritorna il privacy notice, privacy impact assessment o questionnaire in cache o recupera la versione più recente se refresh è true
  loadPrivacyNotice: (
    appUUID: string,
    force: boolean,
  ) => Promise<PrivacyNotice | null | undefined>;
  loadPIA: (appUUID: string, force: boolean) => Promise<PIA | null | undefined>;
  loadQuestionnaire: (
    appUUID: string,
    force: boolean,
  ) => Promise<Questionnaire | null | undefined>;

  //da valutare se mettere in un hook separato, se lo faccio devo però esporre load apps
  claimManagedApplication: (appUUID: string) => Promise<boolean | undefined>;
  assignDpoToManagedApplication: (
    appUUID: string,
    dpoUUID: string,
  ) => Promise<boolean | undefined>;
  ///

  //permette di forzare un aggiornamento del backend della parte apps
  syncApps: () => Promise<void>;
};

const AppsContext = React.createContext<AppsContextValue | undefined>(
  undefined,
);

//dove mettere tutte le funzioni ed è quello da importare in react che wrappa tutto
export function AppsProvider({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const { current_home_uuid, loadingHomes } = useHome();

  const [apps, setApps] = useState<AppModel[] | undefined>(undefined);
  const [PrivacyNoticeByAppUUID, setPrivacyNoticeByAppUUID] = useState<
    Record<string, PrivacyNotice | null | undefined>
  >({});
  const [PIAByAppUUID, setPIAByAppUUID] = useState<
    Record<string, PIA | null | undefined>
  >({});
  const [QuestionnaireByAppUUID, setQuestionnaireByAppUUID] = useState<
    Record<string, Questionnaire | null | undefined>
  >({});
  const [selectedAppUUID, setInnerSelectedAppUUID] = useState<
    string | undefined
  >(undefined);

  const [loadingApps, setLoadingApps] = useState(true);
  const [updatingApps, setUpdatingApps] = useState(false);
  const [errorApps, setErrorApps] = useState<string | undefined>(undefined);
  const [errorUpdatingApps, setErrorUpdatingApps] = useState<
    string | undefined
  >(undefined);

  const setSelectedAppUUID = useCallback((uuid: string | undefined) => {
    //possiamo aggiungere logica extra
    setInnerSelectedAppUUID(uuid);
  }, []);

  const selectedApp = useMemo<AppModel | undefined>(() => {
    if (!user) return undefined;
    if (!apps) return undefined;

    if (selectedAppUUID) {
      const selectedApp = apps.find((app) => app.uuid === selectedAppUUID);
      return selectedApp;
    } else {
      return undefined;
    }
  }, [apps, selectedAppUUID]);

  const managedApps = useMemo<AppModel[]>(() => {
    if (!user) return [];
    const list = apps ?? [];

    if (user.role === Role.DataSubject) return list;

    if (user.role === Role.DatController) {
      return list.filter(
        (app) =>
          app.data_controllers?.some((dc) => dc.uuid === user.uuid) ?? false,
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
      setPIAByAppUUID({});
      setQuestionnaireByAppUUID({});
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
    } catch (err) {
      setLoadingApps(false);
      setErrorApps(err instanceof Error ? err.message : "Errore inatteso");
    }
  }, [current_home_uuid, user?.role]);

  const syncApps = useCallback(async () => {
    if (!user) return;

    setUpdatingApps(true);
    setErrorUpdatingApps(undefined);

    try {
      await updateCatalogApplications();
    } catch (err) {
      setErrorUpdatingApps(
        err instanceof Error ? err.message : "Errore inatteso",
      );
    } finally {
      setUpdatingApps(false);
    }
  }, [user]);

  const loadPrivacyNotice = useCallback(
    async (
      appUUID: string,
      force: boolean,
    ): Promise<PrivacyNotice | null | undefined> => {
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
        setPrivacyNoticeByAppUUID((prev) => ({ ...prev, [appUUID]: res })); //può essere a questo punto o un valore o un null
        //dobbiamo anche aggiornare il flag dell'app che ci dice se il privacy notice è disponibile o no
        //managed apps gestito con use memo si ricarica da solo
        //se res è null significa che non c'è
        setApps((prev) =>
          prev?.map((app) =>
            app.uuid === appUUID
              ? {
                  ...app,
                  pn_status: res
                    ? DocumentStatus.Available
                    : DocumentStatus.Missing,
                }
              : app,
          ),
        );
        return res;
      } catch (err) {
        //vedere cosa fare dell'errore
        return undefined; //rimesso a undefined perchè non è stato caricato correttamente
      }
    },
    [user, managedApps, PrivacyNoticeByAppUUID],
  );

  const loadPIA = useCallback(
    async (
      appUUID: string,
      force: boolean,
    ): Promise<PIA | null | undefined> => {
      if (!user) return undefined;

      //ritorna undefined se il data controller non la gestisce
      if (user.role !== Role.DataSubject) {
        const isManaged = managedApps.some((app) => app.uuid === appUUID);
        if (!isManaged) {
          return undefined;
        }
      }

      if (force == false) {
        const cached = PIAByAppUUID[appUUID];
        if (cached !== undefined) {
          return cached;
        }
      }

      //se non presente in cache la recuperiamo
      try {
        const res = await handleGetPrivacyImpactAssessment(appUUID);
        setPIAByAppUUID((prev) => ({ ...prev, [appUUID]: res })); //può essere a questo punto o un valore o un null
        setApps((prev) =>
          prev?.map((app) =>
            app.uuid === appUUID
              ? {
                  ...app,
                  pia_status: res
                    ? DocumentStatus.Available
                    : DocumentStatus.Missing,
                }
              : app,
          ),
        );
        return res;
      } catch (err) {
        //vedere cosa fare dell'errore
        return undefined; //rimesso a undefined perchè non è stato caricato correttamente
      }
    },
    [user, managedApps, PIAByAppUUID],
  );

  const loadQuestionnaire = useCallback(
    async (
      appUUID: string,
      force: boolean,
    ): Promise<Questionnaire | null | undefined> => {
      if (!user) return undefined;

      //ritorna undefined se il data controller non la gestisce
      if (user.role !== Role.DataSubject) {
        const isManaged = managedApps.some((app) => app.uuid === appUUID);
        if (!isManaged) {
          return undefined;
        }
      }

      if (force == false) {
        const cached = QuestionnaireByAppUUID[appUUID];
        if (cached !== undefined) {
          return cached;
        }
      }

      //se non presente in cache la recuperiamo
      try {
        const res = await handleGetQuestionnaireByApplication(appUUID);
        setQuestionnaireByAppUUID((prev) => ({ ...prev, [appUUID]: res })); //può essere a questo punto o un valore o un null
        setApps((prev) =>
          prev?.map((app) =>
            app.uuid === appUUID
              ? {
                  ...app,
                  evaluation: res?.application_evaluation,
                  questionnaire_summary: res?.questionnaire_summary,
                }
              : app,
          ),
        );
        return res;
      } catch (err) {
        //vedere cosa fare dell'errore
        return undefined; //rimesso a undefined perchè non è stato caricato correttamente
      }
    },
    [user, managedApps, QuestionnaireByAppUUID],
  );

  const claimManagedApplication = useCallback(
    async (appUUID: string): Promise<boolean | undefined> => {
      if (!user) return undefined;
      if (user.role !== Role.DatController) return undefined;

      const created = await claimApplicationAsDataController(appUUID);
      await loadApps();
      return created;
    },
    [loadApps, user],
  );

  const assignDpoToManagedApplication = useCallback(
    async (appUUID: string, dpoUUID: string): Promise<boolean | undefined> => {
      if (!user) return undefined;
      if (user.role !== Role.DatController) return undefined;

      const created = await assignDpoToApplication(appUUID, dpoUUID);
      await loadApps();
      return created;
    },
    [loadApps, user],
  );

  //per ottimizzare il caricamento riguardare meglio
  const value = useMemo<AppsContextValue>(
    () => ({
      apps,
      managedApps,
      PrivacyNoticeByAppUUID,
      PIAByAppUUID,
      QuestionnaireByAppUUID,
      loadingApps,
      updatingApps,
      errorApps,
      errorUpdatingApps,
      selectedAppUUID,
      selectedApp,
      syncApps,
      claimManagedApplication,
      assignDpoToManagedApplication,
      loadPrivacyNotice,
      loadPIA,
      loadQuestionnaire,
      setSelectedAppUUID,
      reloadApps: loadApps,
    }),
    [
      apps,
      managedApps,
      PrivacyNoticeByAppUUID,
      PIAByAppUUID,
      QuestionnaireByAppUUID,
      loadingApps,
      updatingApps,
      errorApps,
      errorUpdatingApps,
      selectedAppUUID,
      selectedApp,
      syncApps,
      claimManagedApplication,
      assignDpoToManagedApplication,
      loadPrivacyNotice,
      loadPIA,
      loadQuestionnaire,
      setSelectedAppUUID,
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
