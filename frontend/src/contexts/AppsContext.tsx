import React, { useCallback, useContext, useEffect, useMemo, useState, } from "react";
import { useAuth } from "./AuthContext";
import { AppModel, CreateApplicationRequest, DocumentStatus, SyncMessage } from "../models/app";
import { fetchApplications, refreshInstalledApplications, createApplicationByDataController } from "../services/ApplicationService";
import { useHome } from "./HomeContext";
import { PrivacyNotice } from "../models/privacy_notice";
import { handleFetchPrivacyNotice } from "../services/PrivacyNoticeService";
import { handleGetPrivacyImpactAssessment } from "../services/PrivacyImpactAssessmentService";
import { PIA } from "../models/PIA";
import { Questionnaire } from "../models/question";
import { handleGetQuestionnaireByApplication } from "../services/QuestionnaireService";
import { ConsentModel } from "../models/available_consent";
import { fetchAvailableConsentsByApplication, fetchConsentsStateBySmartHomeAndApplication } from "../services/AvailableConsentService";
//tutti i parametri del contesto che possono essere comodi e usati in tanti componenti diversi
//Questo è il contesto delle app dove sono presenti tutte le informazioni utili usate da più parti dell'UI e i metodi di sync e loading delle informazioni dal database
type AppsContextValue = {

  apps: AppModel[] | undefined; //per data subject sono le installed apps, per data controller / dpo sono le managed apps
  selectedAppUUID: string | undefined; //è l'uuid dell'app selezionata dal sistema Catalog/InstalledApp/PIA/PN
  selectedApp: AppModel | undefined; //l'app selezionata corrente dal sistema Catalog/InstalledApp/PIA/PN
  loadingApps: boolean; //indica se è in corso un fetch delle apps dal backend
  errorApps: string | undefined; //indica se c'è stato un errore durante il fetch di qualcosa delle app dal backend
  updatingApps: boolean; //indica se è in corso un update delle apps nel backend (attraverso un refresh)
  appsSyncMessages: SyncMessage[];
  PrivacyNoticeByAppUUID: Record<string, PrivacyNotice | null | undefined> //record cache dei PN
  PIAByAppUUID: Record<string, PIA | null | undefined> //record cache dei PIA
  QuestionnaireByAppUUID: Record<string, Questionnaire | null | undefined>; //
  ConsentStatesByAppUUID: Record<string, ConsentModel[] | undefined>; //record cache consensi per app (DS e DC/DPO)
  isSelectedAppOwner: boolean;

  //espone modo per cambiare app selezionata
  setSelectedAppUUID: (uuid: string | undefined) => void

  //ritornano il PN/PIA/Questonario in cache o recupera la versione più recente se refresh è true
  //inoltre si occupa di aggiornare lo status di validità del PN/PIA/Questionario in Apps quando force è true
  loadPrivacyNotice: (appUUID: string, force: boolean) => Promise<PrivacyNotice | null | undefined>
  loadPIA: (appUUID: string, force: boolean) => Promise<PIA | null | undefined>
  loadQuestionnaire: (appUUID: string, force: boolean) => Promise<Questionnaire | null | undefined>;
  loadApps: (applicationUUID?: string, force?: boolean) => Promise<AppModel[] | undefined>;
  loadConsentsByApplication: (appUUID: string, force: boolean) => Promise<ConsentModel[] | undefined>;


  createManagedApplication: (payload: CreateApplicationRequest) => Promise<AppModel | undefined>;

  //permette di forzare un aggiornamento apps per Data Subject
  syncApps: () => Promise<void>;
};

const AppsContext = React.createContext<AppsContextValue | undefined>(undefined);

//dove mettere tutte le funzioni ed è quello da importare in react che wrappa tutto
export function AppsProvider({ children }: { children: React.ReactNode }) {
  const { user, loading, isDataSubject, isDataController } = useAuth();
  const { current_home_uuid, loadingHomes } = useHome();

  const [apps, setApps] = useState<AppModel[] | undefined>(undefined);
  const [PrivacyNoticeByAppUUID, setPrivacyNoticeByAppUUID] = useState<Record<string, PrivacyNotice | null | undefined>>({});
  const [PIAByAppUUID, setPIAByAppUUID] = useState<Record<string, PIA | null | undefined>>({});
  const [QuestionnaireByAppUUID, setQuestionnaireByAppUUID] = useState<Record<string, Questionnaire | null | undefined>>({});
  const [ConsentStatesByAppUUID, setConsentStatesByAppUUID] = useState<Record<string, ConsentModel[] | undefined>>({});
  const [selectedAppUUID, setInnerSelectedAppUUID] = useState<string | undefined>(undefined);

  const [loadingApps, setLoadingApps] = useState(true);
  const [updatingApps, setUpdatingApps] = useState(false);
  const [errorApps, setErrorApps] = useState<string | undefined>(undefined);
  const [appsSyncMessages, setAppsSyncMessages] = useState<SyncMessage[]>([]);

  const setSelectedAppUUID = useCallback((uuid: string | undefined) => {
    //possiamo aggiungere logica extra
    setInnerSelectedAppUUID(uuid);
  }, []);


  //sync local database if information on the backend changes
  useEffect(() => {

    if (loading) return;
    if (!user) {
      setApps(undefined);
      setLoadingApps(false);
      setUpdatingApps(false);
      setErrorApps(undefined);
      setAppsSyncMessages([]);
      setPrivacyNoticeByAppUUID({});
      setPIAByAppUUID({});
      setQuestionnaireByAppUUID({});
      setConsentStatesByAppUUID({});
      return;
    }

    if (isDataSubject && loadingHomes) return;

    loadApps();
  }, [loading, updatingApps, user?.uuid, isDataSubject, current_home_uuid, loadingHomes]);

  //invalidiamo la cache consensi quando cambia casa corrente (stato given dipende dalla home)
  useEffect(() => {
    setConsentStatesByAppUUID({});
  }, [current_home_uuid, user?.uuid]);


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

  const isSelectedAppOwner = useMemo<boolean>(() => {
    if (!user) return false;
    if (!selectedApp) return false;
    return selectedApp.owner?.uuid === user.uuid;
  }, [selectedApp, user?.uuid]);

  const loadApps = useCallback(async (applicationUUID?: string, force?: boolean): Promise<AppModel[] | undefined> => {
    
    const loadingAllApps = !applicationUUID;

    if (loadingAllApps) {
      setLoadingApps(true);
    }
    setErrorApps(undefined);

    try {

      if (applicationUUID && force === false) {
        const cached = (apps ?? []).find((app) => app.uuid === applicationUUID);
        if (cached !== undefined) {
          return [cached];
        }
      }

      const res = await fetchApplications(
        isDataSubject ? (current_home_uuid ?? null) : undefined,
        applicationUUID,
      );

      if (!res) {
        if (loadingAllApps) {
          setApps([]);
          setErrorApps("Impossibile caricare le applicazioni.");
        }
        return undefined;
      }

      if (loadingAllApps) {
        setApps(res);
        return res;
      }

      const loadedApplication = res[0];
      if (!loadedApplication) return res;

      setApps((prev) => {

        //caso non c'è nessun elemento -> 1 sola app
        if (!prev) return [loadedApplication];

        //vediamo se esisteva
        const exists = prev.some((app) => app.uuid === loadedApplication.uuid);

        //caso prima non esiste, la aggiungiamo all'inizio
        if (!exists) return [loadedApplication, ...prev];

        //caso prima esisteva, la aggiorniamo
        return prev.map((app) => (app.uuid === loadedApplication.uuid ? loadedApplication : app));
      });
      
      return res;
    }
    catch (err) {
      setErrorApps(err instanceof Error ? err.message : "Unexpected Error");
      return undefined;
    }
    finally {
      if (loadingAllApps) {
        setLoadingApps(false);
      }
    }
  }, [apps, current_home_uuid, user?.uuid, isDataSubject]);

  const syncApps = useCallback(async () => {
    if (!user) return;
    if (!isDataSubject) return;

    setUpdatingApps(true);
    setAppsSyncMessages([]);

    try {
      const refreshResult = await refreshInstalledApplications();
      setAppsSyncMessages((refreshResult?.warnings ?? []).map((warning) => ({ level: "warning", text: warning })));
    } catch (err) {
      setAppsSyncMessages([{ level: "error", text: err instanceof Error ? err.message : "Unexpected Error" }]);
    } finally {
      setUpdatingApps(false);
    }
  }, [user?.uuid, isDataSubject]);

  const loadPrivacyNotice = useCallback(async (appUUID: string, force: boolean,): Promise<PrivacyNotice | null | undefined> => {
    if (!user) return undefined;

    if (force == false) {
      const cached = PrivacyNoticeByAppUUID[appUUID];
      if (cached !== undefined) {
        return cached;
      }
      //se era undefined proviamo di nuovo a caricarlo
    }

    //se non presente in cache la recuperiamo
    try {
      const res = await handleFetchPrivacyNotice(appUUID, user.role);
      setPrivacyNoticeByAppUUID(prev => ({ ...prev, [appUUID]: res })); //può essere a questo punto o un valore o un null
      //dobbiamo anche aggiornare il flag dell'app che ci dice se il privacy notice è disponibile o no
      //managed apps gestito con use memo si ricarica da solo
      //se res è null significa che non c'è
      setApps(prev => prev?.map(app => app.uuid === appUUID ? { ...app, pn_status: res ? DocumentStatus.Available : DocumentStatus.Missing } : app))
      return res;
    }
    catch (err) {
      setErrorApps(err instanceof Error ? err.message : "Unexpected Error")
      return undefined //rimesso a undefined perchè non è stato caricato correttamente
    }
  },
    [user, PrivacyNoticeByAppUUID],
  );

  const loadPIA = useCallback(async (appUUID: string, force: boolean): Promise<PIA | null | undefined> => {
    if (!user) return undefined;

    if (force == false) {
      const cached = PIAByAppUUID[appUUID];
      if (cached !== undefined) {
        return cached;
      }
      //se era undefined proviamo di nuovo a caricarlo
    }

    //se non presente in cache la recuperiamo
    try {
      const res = await handleGetPrivacyImpactAssessment(appUUID);
      setPIAByAppUUID(prev => ({ ...prev, [appUUID]: res })); //può essere a questo punto o un valore o un null
      setApps(prev => prev?.map(app => app.uuid === appUUID ? { ...app, pia_status: res ? DocumentStatus.Available : DocumentStatus.Missing } : app))
      return res;
    }
    catch (err) {
      setErrorApps(err instanceof Error ? err.message : "Unexpected Error")
      return undefined //rimesso a undefined perchè non è stato caricato correttamente
    }
  },
    [user, PIAByAppUUID],
  );

  const loadQuestionnaire = useCallback(async (appUUID: string, force: boolean): Promise<Questionnaire | null | undefined> => {
    if (!user) return undefined;

    if (force == false) {
      const cached = QuestionnaireByAppUUID[appUUID];
      if (cached !== undefined) {
        return cached;
      }
      //se era undefined proviamo di nuovo a caricarlo
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
      setErrorApps(err instanceof Error ? err.message : "Unexpected Error")
      return undefined; //rimesso a undefined perchè non è stato caricato correttamente
    }
  },
    [user, QuestionnaireByAppUUID],
  );

  const loadConsentsByApplication = useCallback(async (appUUID: string, force: boolean): Promise<ConsentModel[] | undefined> => {
    if (!user) return undefined;

    if (force == false) {
      const cached = ConsentStatesByAppUUID[appUUID];
      if (cached !== undefined) {
        return cached;
      }
      //se era undefined proviamo di nuovo a caricarlo
    }

    try {

      if (isDataSubject) {
        if (!current_home_uuid) return undefined;
        const consentStates = await fetchConsentsStateBySmartHomeAndApplication(current_home_uuid, appUUID);
        setConsentStatesByAppUUID((prev) => ({ ...prev, [appUUID]: consentStates }));
        return consentStates;
      }

      const availableConsents = await fetchAvailableConsentsByApplication(appUUID);
      setConsentStatesByAppUUID((prev) => ({ ...prev, [appUUID]: availableConsents }));
      return availableConsents;

    } catch (err) {
      setErrorApps(err instanceof Error ? err.message : "Unexpected Error")
      return undefined;
    }
  },
    [user, current_home_uuid, ConsentStatesByAppUUID],
  );

  const createManagedApplication = useCallback(async (payload: CreateApplicationRequest): Promise<AppModel | undefined> => {
    if (!user) return undefined;
    if (!isDataController) return undefined;

    const createdApp = await createApplicationByDataController(payload);
    //filter lo teniamo per evitare problemi durante 2 aggiornamenti concorrenti di apps
    setApps((prev) => [createdApp,...(prev ?? []).filter((app) => app.uuid !== createdApp.uuid)]);
    setSelectedAppUUID(createdApp.uuid);
    return createdApp;
  },
    [setSelectedAppUUID, user?.uuid, isDataController],
  );


  //per ottimizzare il caricamento riguardare meglio
  const value = useMemo<AppsContextValue>(
    () => ({
      apps,
      PrivacyNoticeByAppUUID,
      PIAByAppUUID,
      QuestionnaireByAppUUID,
      ConsentStatesByAppUUID,
      isSelectedAppOwner,
      loadingApps,
      updatingApps,
      errorApps,
      appsSyncMessages,
      selectedAppUUID,
      selectedApp,
      syncApps,
      createManagedApplication,
      loadPrivacyNotice,
      loadPIA,
      loadQuestionnaire,
      loadApps,
      loadConsentsByApplication,
      setSelectedAppUUID,
    }),
    [
      apps,
      PrivacyNoticeByAppUUID,
      PIAByAppUUID,
      QuestionnaireByAppUUID,
      ConsentStatesByAppUUID,
      isSelectedAppOwner,
      loadingApps,
      updatingApps,
      errorApps,
      appsSyncMessages,
      selectedAppUUID,
      selectedApp,
      syncApps,
      createManagedApplication,
      loadPrivacyNotice,
      loadPIA,
      loadQuestionnaire,
      loadApps,
      loadConsentsByApplication,
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
