import { useEffect, useState } from "react";
import { Button, Card, Form } from "react-bootstrap";
import { useAuth } from "./Authentication/AuthContext";
import { Role, User } from "../models/user";
import { useApp } from "./AppsContext";
import { fetchDataProtectionOfficers } from "../services/UserService";
import { DocumentStatus } from "../models/app";


function AppAssignmentPanel() {


    const { user } = useAuth();
    const {selectedApp, claimManagedApplication,assignDpoToManagedApplication, managedApps, selectedAppUUID} = useApp();


    const isDataController = user?.role === Role.DatController;

    
    //magari si può semplificare anche questo con un flag se managed oppure no invece di guardare in managedApps
    const isManagedByMe = selectedApp && managedApps.some((app) => app.uuid === selectedAppUUID);

    
    const [dpos, setDpos] = useState<User[] | undefined>(undefined);
    const [loadingDpos, setLoadingDpos] = useState(false);
    const [selectedDpoUuid, setSelectedDpoUuid] = useState<string>("");

    //per disabilitare tasto claim data controller e evitare doppio click
    const [claimingApp, setClaimingApp] = useState(false);

    //per disabilitare tasto dpo per evitare doppio click 
    const [assigningDpo, setAssigningDpo] = useState(false);

    //per tutti gli errori di gestione Data controller / DPO
    const [managementError, setManagementError] = useState<string | undefined>(undefined);



    useEffect(() => {
        if (!isDataController) {
            setDpos(undefined);
            setSelectedDpoUuid("");
            setManagementError(undefined);
            return;
        }

        let cancelled = false;
        setLoadingDpos(true);

        fetchDataProtectionOfficers()
            .then((res) => {
                if (cancelled) return;
                const list = res ?? [];
                setDpos(list);
                setSelectedDpoUuid((prev) => prev || (list[0]?.uuid ?? ""));
            })
            .catch((err) => {
                if (cancelled) return;
                setManagementError(err instanceof Error ? err.message : "Errore inatteso");
                setDpos([]);
            })
            .finally(() => {
                if (cancelled) return;
                setLoadingDpos(false);
            });

        return () => {
            cancelled = true;
        };
    }, [isDataController, user?.uuid]);



    const onClaimManagedApplication = async () => {
        if (!selectedAppUUID) return;
        setManagementError(undefined);
        setClaimingApp(true);
        try {
            await claimManagedApplication(selectedAppUUID);
        } catch (err) {
            setManagementError(err instanceof Error ? err.message : "Errore inatteso");
        } finally {
            setClaimingApp(false);
        }
    };

    const onAssignDpo = async () => {
        if (!selectedAppUUID) return;
        if (!selectedDpoUuid) {
            setManagementError("Seleziona un DPO.");
            return;
        }
        setManagementError(undefined);
        setAssigningDpo(true);
        try {
            await assignDpoToManagedApplication(selectedAppUUID, selectedDpoUuid);
        } catch (err) {
            setManagementError(err instanceof Error ? err.message : "Errore inatteso");
        } finally {
            setAssigningDpo(false);
        }
    };



    return (
        <>
        <Card className="p-0">
            <Card.Body className="d-flex flex-column gap-2">
                <strong>Management</strong>

                {managementError ? (
                    <div className="text-danger small">
                        {managementError}
                    </div>
                ) : undefined}

                {!isManagedByMe ? (
                    <Button
                        size="sm"
                        variant="primary"
                        disabled={claimingApp}
                        onClick={onClaimManagedApplication}
                    >
                        {claimingApp ? "Claiming…" : "Claim application"}
                    </Button>
                ) : selectedApp?.dpo ? (
                    <div className="text-muted small">
                        DPO già assegnato:{" "}
                        {`${selectedApp.dpo.firstname} ${selectedApp.dpo.lastname}`.trim() ||
                            selectedApp.dpo.email}
                    </div>
                ) : (
                    <>
                        <Form.Select
                            size="sm"
                            value={selectedDpoUuid}
                            onChange={(e) => setSelectedDpoUuid(e.target.value)}
                            disabled={loadingDpos || assigningDpo || !dpos?.length}
                        >
                            {(!dpos || dpos.length === 0) && (
                                <option value="" disabled>
                                    {loadingDpos ? "Loading DPOs…" : "No DPOs available"}
                                </option>
                            )}
                            {dpos?.map((dpo) => (
                                <option key={dpo.uuid} value={dpo.uuid}>
                                    {`${dpo.firstname} ${dpo.lastname}`.trim() ||
                                        dpo.email}
                                </option>
                            ))}
                        </Form.Select>

                        <Button
                            size="sm"
                            variant="outline-primary"
                            disabled={
                                assigningDpo || loadingDpos || !selectedDpoUuid
                            }
                            onClick={onAssignDpo}
                        >
                            {assigningDpo ? "Assigning…" : "Assign DPO"}
                        </Button>
                    </>
                )}
            </Card.Body>
        </Card>
        </>
    );
}

export { AppAssignmentPanel };
