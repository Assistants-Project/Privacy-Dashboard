import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useHome } from "../contexts/HomeContext";
import { RequestStatus } from "../models/request";
import { Role } from "../models/user";
import { fetchRequestsHome, fetchRequestsInbox, RequestListItem } from "../services/RightsService";

type UseRightsRequestsResult = {
  requests: RequestListItem[] | undefined;
  loadingRequests: boolean;
  errorRequests: string | undefined;
  loadRequests: () => Promise<void>;
};

//hook per caricare le requests (rights) in base all'utente loggato:
//Data Subject: requests della casa corrente
//Data Controller / DPO: inbox delle requests ricevute
function useRightsRequests(statusFilter: RequestStatus | undefined): UseRightsRequestsResult {
  const { user, loading } = useAuth();
  const { current_home_uuid, loadingHomes } = useHome();

  const isDataSubject = user?.role === Role.DataSubject;

  const [requests, setRequests] = useState<RequestListItem[] | undefined>(undefined,);
  const [loadingRequests, setLoadingRequests] = useState<boolean>(true);
  const [errorRequests, setErrorRequests] = useState<string | undefined>(undefined,);

  const loadRequests = useCallback(async () => {
    if (loading) return;

    if (!user) {
      setRequests(undefined);
      setLoadingRequests(false);
      setErrorRequests(undefined);
      return;
    }

    //per data subject aspettiamo che le home siano caricate, altrimenti non possiamo sapere current_home_uuid
    if (isDataSubject && loadingHomes) return;

    setLoadingRequests(true);
    setErrorRequests(undefined);

    try {

      let res: RequestListItem[] | undefined;

      if (isDataSubject) {
        if (!current_home_uuid) {
          res = [];
        } else {
          res = await fetchRequestsHome(current_home_uuid, statusFilter);
        }
      } else {
        res = await fetchRequestsInbox(statusFilter);
      }

      setRequests(res ?? []);

    } catch (err) {

      setErrorRequests(err instanceof Error ? err.message : "Errore inatteso");
      setRequests(undefined);

    } finally {
      setLoadingRequests(false);
    }
    //ricarichiamo automaticamente quando cambia utente, home corrente o filtro stato
  }, [loading, user?.uuid, isDataSubject, current_home_uuid, loadingHomes, statusFilter]);


  useEffect(() => {
    void loadRequests();
  }, [loadRequests]); //si ricarica quando cambia la firma della funzione quindi ogni qual volta accade quello indicato sopra

  return { requests, loadingRequests, errorRequests, loadRequests };
}

export { useRightsRequests };
