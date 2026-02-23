import { useState } from "react";
import { Button, Card, Col, Form, Row } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { useApp } from "../../contexts/AppsContext";

function AppAssignmentPanel() {

    const { user } = useAuth();
    const {
        selectedApp,
        assignDpoToManagedApplication,
        addManagerToManagedApplication,
        removeManagerFromManagedApplication,
        selectedAppUUID,
    } = useApp();


    const isOwner = !!selectedApp && !!user && selectedApp.owner.uuid === user.uuid;
    const managers = selectedApp
        ? selectedApp.data_controllers.filter((dc) => dc.uuid !== selectedApp.owner.uuid)
        : [];

    const [dpoEmail, setDpoEmail] = useState<string>("");
    const [managerEmail, setManagerEmail] = useState<string>("");

    //per disabilitare tasto dpo per evitare doppio click 
    const [assigningDpo, setAssigningDpo] = useState(false);
    const [addingManager, setAddingManager] = useState(false);
    const [removingManagerEmail, setRemovingManagerEmail] = useState<string>("");

    //per tutti gli errori di gestione Data controller / DPO
    const [managementError, setManagementError] = useState<string | undefined>(undefined);



    const onAssignDpo = async () => {
        if (!selectedAppUUID) return;
        const normalizedDpoEmail = dpoEmail.trim();
        if (!normalizedDpoEmail) {
            setManagementError("Insert a DPO email.");
            return;
        }
        setManagementError(undefined);
        setAssigningDpo(true);
        try {
            await assignDpoToManagedApplication(selectedAppUUID, normalizedDpoEmail);
            setDpoEmail("");
        } catch (err) {
            setManagementError(err instanceof Error ? err.message : "Errore inatteso");
        } finally {
            setAssigningDpo(false);
        }
    };

    const onAddManager = async () => {
        if (!selectedAppUUID) return;
        const normalizedEmail = managerEmail.trim();
        if (!normalizedEmail) {
            setManagementError("Insert a Data Controller email.");
            return;
        }
        setManagementError(undefined);
        setAddingManager(true);
        try {
            await addManagerToManagedApplication(selectedAppUUID, normalizedEmail);
            setManagerEmail("");
        } catch (err) {
            setManagementError(err instanceof Error ? err.message : "Errore inatteso");
        } finally {
            setAddingManager(false);
        }
    };

    const onRemoveManager = async (userEmail: string) => {
        if (!selectedAppUUID) return;
        setManagementError(undefined);
        setRemovingManagerEmail(userEmail);
        try {
            await removeManagerFromManagedApplication(selectedAppUUID, userEmail);
        } catch (err) {
            setManagementError(err instanceof Error ? err.message : "Errore inatteso");
        } finally {
            setRemovingManagerEmail("");
        }
    };



    return (
        <>
        <Card className="p-0">
            <Card.Body>
                <strong>Management</strong>
                <div className="mt-2" />
                {managementError ? (
                    <div className="text-danger small">
                        {managementError}
                    </div>
                ) : undefined}

                {!isOwner ? (
                    <div className="text-muted small">
                        Only the owner can manage managers and DPO assignment.
                    </div>
                ) : (
                    <>
                    <div className="small fw-semibold mb-2">Managers</div>
                    <Row className="mb-2">
                        <Col>
                            <Form.Control
                                size="sm"
                                placeholder="Data Controller email"
                                value={managerEmail}
                                onChange={(e) => setManagerEmail(e.target.value)}
                                disabled={addingManager || assigningDpo}
                            />
                        </Col>
                        <Col className="ps-0">
                            <Button
                                size="sm"
                                variant="outline-primary"
                                disabled={addingManager || assigningDpo || managerEmail.trim() === ""}
                                onClick={onAddManager}
                            >
                                {addingManager ? "Adding…" : "Add"}
                            </Button>
                        </Col>
                    </Row>

                    {managers.length === 0 ? (
                        <div className="text-muted small mb-3">No managers assigned.</div>
                    ) : (
                        <div className="d-flex flex-column gap-2 mb-3">
                            {managers.map((manager) => (
                                <div key={manager.uuid} className="d-flex align-items-center justify-content-between border rounded p-2">
                                    <div className="small">
                                        {`${manager.firstname} ${manager.lastname}`.trim() || manager.email}
                                    </div>
                                    <Button
                                        size="sm"
                                        variant="outline-danger"
                                        disabled={!!removingManagerEmail}
                                        onClick={() => onRemoveManager(manager.email)}
                                    >
                                        {removingManagerEmail === manager.email ? "Removing…" : "Remove"}
                                    </Button>
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="small fw-semibold mb-2">DPO</div>
                    {selectedApp?.dpo ? (
                        <div className="text-muted small mb-2">
                            Assigned DPO:{" "}
                            {`${selectedApp.dpo.firstname} ${selectedApp.dpo.lastname}`.trim() ||
                                selectedApp.dpo.email}
                        </div>
                    ) : undefined}

                    <Row>
                        <Col>
                            <Form.Control
                                size="sm"
                                placeholder="DPO email"
                                value={dpoEmail}
                                onChange={(e) => setDpoEmail(e.target.value)}
                                disabled={assigningDpo || addingManager}
                            />
                        
                        </Col>
                        <Col className="ps-0"> 
                        <Button
                            size="sm"
                            variant="outline-primary"
                            disabled={assigningDpo || addingManager || dpoEmail.trim() === ""}
                            onClick={onAssignDpo}
                        >
                            {assigningDpo ? "Assigning…" : "Assign DPO"}
                        </Button>
                        
                        </Col>
                    </Row>
                    </>
                )}
            </Card.Body>
        </Card>
        </>
    );
}

export { AppAssignmentPanel };
