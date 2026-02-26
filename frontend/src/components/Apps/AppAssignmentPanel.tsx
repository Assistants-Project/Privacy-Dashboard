import { useState } from "react";
import { Button, Card, Col, Form, Modal, Row, Spinner } from "react-bootstrap";
import { XCircle } from "react-bootstrap-icons";
import { useAuth } from "../../contexts/AuthContext";
import { useApp } from "../../contexts/AppsContext";
import { User } from "../../models/user";
import { addDataControllerManagerToApplication, assignDpoToApplication, removeDataControllerManagerFromApplication, removeDpoFromApplication } from "../../services/ApplicationService";

function AppAssignmentPanel() {
  const { user, isDataController } = useAuth();
  const { selectedApp, selectedAppUUID, loadApps } = useApp();

  const [showAddManagerModal, setShowAddManagerModal] = useState(false);
  const [showAssignDpoModal, setShowAssignDpoModal] = useState(false);

  const [managerEmail, setManagerEmail] = useState("");
  const [dpoEmail, setDpoEmail] = useState("");

  const [addingManager, setAddingManager] = useState(false);
  const [assigningDpo, setAssigningDpo] = useState(false);
  const [removingManagerEmail, setRemovingManagerEmail] = useState("");

  const [controllersError, setControllersError] = useState<string | undefined>(undefined);
  const [dpoError, setDpoError] = useState<string | undefined>(undefined);

  if (!selectedApp) return null;

  const canManageAssignments = isDataController && !!user && selectedApp.owner.uuid === user.uuid;
  const managers = selectedApp.data_controllers.filter((user) => user.uuid !== selectedApp.owner.uuid);

  const userLabel = (user: User): string => `${user.firstname} ${user.lastname}`.trim() || user.email;

  const onAddManager = async () => {
    if (!selectedAppUUID) return;

    const normalizedEmail = managerEmail.trim();
    if (!normalizedEmail) {
      setControllersError("Insert a Data Controller email");
      return;
    }
    if (normalizedEmail === selectedApp.owner.email) {
      setControllersError("Owner is already part of controllers");
      return;
    }

    setControllersError(undefined);
    setAddingManager(true);

    try {
      await addDataControllerManagerToApplication(selectedAppUUID, normalizedEmail);
      await loadApps(selectedAppUUID, true);
      setManagerEmail("");
    } catch (err) {
      setControllersError(err instanceof Error ? err.message : "Unexpected Error");
    } finally {
      setAddingManager(false);
    }
  };

  const onRemoveManager = async (email: string) => {
    if (!selectedAppUUID) return;

    setControllersError(undefined);
    setRemovingManagerEmail(email);

    try {
      await removeDataControllerManagerFromApplication(selectedAppUUID, email);
      await loadApps(selectedAppUUID, true);
    } catch (err) {
      setControllersError(err instanceof Error ? err.message : "Unexpected Error");
    } finally {
      setRemovingManagerEmail("");
    }
  };

  const onAssignDpo = async () => {
    if (!selectedAppUUID) return;

    const normalizedEmail = dpoEmail.trim();
    if (!normalizedEmail) {
      setDpoError("Insert a DPO email");
      return;
    }

    setDpoError(undefined);
    setAssigningDpo(true);

    try {
      await assignDpoToApplication(selectedAppUUID, normalizedEmail);
      await loadApps(selectedAppUUID, true);
      setDpoEmail("");
      setShowAssignDpoModal(false);
    } catch (err) {
      setDpoError(err instanceof Error ? err.message : "Unexpected Error");
    } finally {
      setAssigningDpo(false);
    }
  };

  const onRemoveDpo = async () => {
    if (!selectedAppUUID || !selectedApp.dpo) return;

    setDpoError(undefined);
    setAssigningDpo(true);

    try {
      await removeDpoFromApplication(selectedAppUUID);
      await loadApps(selectedAppUUID, true);
      setDpoEmail("");
      setShowAssignDpoModal(false);
    } catch (err) {
      setDpoError(err instanceof Error ? err.message : "Unexpected Error");
    } finally {
      setAssigningDpo(false);
    }
  };

  return (
    <>
      <Row xs={1} md={2} className="g-3">
        <Col>
          <Card className="h-100 p-0">
            <Card.Body>
              <Row className="g-2">
                <Col>
                  <h5>Data Controllers</h5>
                </Col>
                {canManageAssignments ? (
                  <Col xs="auto" className="pe-0 mt-0">
                    <Button
                      className="circular-button me-0"
                      style={{ color: "#181d1f" }}
                      disabled={addingManager || !!removingManagerEmail}
                      onClick={() => {
                        setControllersError(undefined);
                        setManagerEmail("");
                        setShowAddManagerModal(true);
                      }}
                      title="Manage managers"
                      aria-label="Manage managers"
                    >
                      <i className="fa-solid fa-pencil" style={{ fontSize: "0.90rem" }}></i>
                    </Button>
                  </Col>
                ) : undefined}

                {selectedApp.data_controllers.length ? (
                  <Col xs={12}>
                    <Row>
                      {selectedApp.data_controllers.map((contact) => {
                        const isMine = contact.uuid === user?.uuid;
                        const isOwnerContact = contact.uuid === selectedApp.owner.uuid;
                        return (
                          <Col xs="auto" className="my-1" key={contact.email}>
                            <div className="d-inline-flex align-items-center border rounded-pill px-3 py-2">
                              {isMine ? (
                                <span className="fs-6 text-primary fw-semibold">Me</span>
                              ) : (
                                <span className="fs-6 text-nowrap">{userLabel(contact)}</span>
                              )}
                              {isOwnerContact ? (
                                <span className="small text-muted ms-1">- Owner</span>
                              ) : undefined}
                            </div>
                          </Col>
                        );
                      })}
                    </Row>
                  </Col>
                ) : (
                  <Col xs={12}>
                    <div className="text-muted mt-4">Not Assigned</div>
                  </Col>
                )}

              </Row>
            </Card.Body>
          </Card>
        </Col>

        <Col>
          <Card className="h-100 p-0">
            <Card.Body>
              <Row className="g-2">
                <Col>
                  <h5>Data Protection Officer</h5>
                </Col>
                {canManageAssignments ? (
                  <Col xs="auto" className="pe-0 mt-0">
                    <Button
                      className="circular-button me-0"
                      style={{ color: "#181d1f" }}
                      disabled={assigningDpo}
                      onClick={() => {
                        setDpoError(undefined);
                        setDpoEmail(selectedApp.dpo?.email ?? "");
                        setShowAssignDpoModal(true);
                      }}
                      title="Manage DPO"
                      aria-label="Manage DPO"
                    >
                      <i className="fa-solid fa-pencil" style={{ fontSize: "0.90rem" }}></i>
                    </Button>
                  </Col>
                ) : undefined}

                {selectedApp.dpo ? (
                  <Col xs={12}>
                    <Row>
                      <Col xs="auto">
                        <div className="d-inline-flex align-items-center gap-2 border rounded-pill px-3 py-2">
                          {selectedApp.dpo.uuid === user?.uuid ? (
                            <span className="fs-6 text-primary fw-semibold">Me</span>
                          ) : (
                            <span className="fs-6 text-nowrap">{userLabel(selectedApp.dpo)}</span>
                          )}
                        </div>
                      </Col>
                    </Row>
                  </Col>
                ) : (
                  <Col xs={12}>
                    <div className="text-muted mt-1">Not Assigned</div>
                  </Col>
                )}

              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Modal show={showAddManagerModal} onHide={() => setShowAddManagerModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Manage Managers</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Row className="g-3">
            <Col xs={12}>
              <div className="small fw-semibold">Current managers</div>
            </Col>
            {managers.length === 0 ? (
              <Col xs={12}>
                <div className="text-muted small">No managers assigned.</div>
              </Col>
            ) : (
              <Col xs={12}>
                <Row className="g-2">
                  {managers.map((manager) => (
                    <Col xs="auto" key={manager.email}>
                      <div className="d-inline-flex align-items-center gap-2 border py-2 px-3 rounded-pill px-2 py-1">
                        <span className="text-nowrap">{userLabel(manager)}</span>
                        <Button
                          size="sm"
                          variant="link"
                          className="text-danger p-0 d-inline-flex align-items-center"
                          style={{ lineHeight: 1 }}
                          disabled={!!removingManagerEmail || addingManager}
                          onClick={() => onRemoveManager(manager.email)}
                          aria-label={`Remove ${userLabel(manager)}`}
                        >
                          {removingManagerEmail === manager.email ? (
                            <span className="d-inline-flex align-items-center gap-1">
                              <Spinner animation="border" size="sm" />
                              Removing
                            </span>
                          ) : (
                            <XCircle size={18} />
                          )}
                        </Button>
                      </div>
                    </Col>
                  ))}
                </Row>
              </Col>
            )}

            <Col xs={12}>
              <Row className="g-2 align-items-start">
                <Col xs={12} md>
                  <Form.Group className="mb-0">
                    <Form.Control
                      type="email"
                      value={managerEmail}
                      onChange={(e) => setManagerEmail(e.target.value)}
                      placeholder="name@example.com"
                      disabled={addingManager}
                    />
                  </Form.Group>
                </Col>
                <Col xs="auto">
                  <Button variant="primary" onClick={onAddManager} disabled={addingManager || managerEmail.trim() === ""}>
                    {addingManager ? (
                      <span className="d-inline-flex align-items-center gap-2">
                        <Spinner animation="border" size="sm" />
                        Adding…
                      </span>
                    ) : "Add"}
                  </Button>
                </Col>
              </Row>
            </Col>
            {controllersError ? (
              <Col xs={12}>
                <div className="text-danger small">{controllersError}</div>
              </Col>
            ) : undefined}
          </Row>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={() => setShowAddManagerModal(false)} disabled={addingManager}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>

      <Modal show={showAssignDpoModal} onHide={() => setShowAssignDpoModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Assign DPO</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group className="mb-0">
            <Form.Label className="small text-muted">DPO email</Form.Label>
            <Form.Control
              type="email"
              value={dpoEmail}
              onChange={(e) => setDpoEmail(e.target.value)}
              placeholder="name@example.com"
              disabled={assigningDpo}
            />
          </Form.Group>
          {dpoError ? <div className="text-danger small mt-2">{dpoError}</div> : undefined}
        </Modal.Body>
        <Modal.Footer>
          {selectedApp.dpo ? (
            <Button variant="outline-danger" onClick={onRemoveDpo} disabled={assigningDpo}>
              {assigningDpo ? (
                <span className="d-inline-flex align-items-center gap-2">
                  <Spinner animation="border" size="sm" />
                  Removing…
                </span>
              ) : "Remove DPO"}
            </Button>
          ) : undefined}
          <Button variant="outline-secondary" onClick={() => setShowAssignDpoModal(false)} disabled={assigningDpo}>
            Cancel
          </Button>
          <Button variant="primary" onClick={onAssignDpo} disabled={assigningDpo || dpoEmail.trim() === ""}>
            {assigningDpo ? (
              <span className="d-inline-flex align-items-center gap-2">
                <Spinner animation="border" size="sm" />
                Assigning…
              </span>
            ) : "Assign"}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}

export { AppAssignmentPanel };
