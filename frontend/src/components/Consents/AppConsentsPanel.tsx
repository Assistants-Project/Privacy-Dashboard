import { useEffect, useMemo, useState } from "react";
import { Button, Card, Col, Form, Modal, Row, Spinner } from "react-bootstrap";
import { CheckCircleFill, Circle, XCircle } from "react-bootstrap-icons";
import { useHome } from "../../contexts/HomeContext";
import { useAuth } from "../../contexts/AuthContext";
import { useApp } from "../../contexts/AppsContext";
import { addAvailableConsentToManagedApplication, giveConsentsInSmartHome, removeAvailableConsentFromManagedApplication } from "../../services/AvailableConsentService";

type AppConsentsPanelProps = {
  onWithdrawConsents?: (consentUuids: string[]) => void;
};

function AppConsentsPanel({ onWithdrawConsents }: AppConsentsPanelProps) {
  const { current_home_uuid } = useHome();
  const { user, isDataSubject, isManagerRole } = useAuth();
  const { selectedApp, selectedAppUUID, ConsentStatesByAppUUID, loadConsents } = useApp();

  const [showManageConsentsModal, setShowManageConsentsModal] = useState(false);
  const [consentInput, setConsentInput] = useState("");

  const [loadingConsents, setLoadingConsents] = useState<boolean>(false);
  const [acceptingAllConsents, setAcceptingAllConsents] = useState<boolean>(false);
  const [givingConsentUuid, setGivingConsentUuid] = useState<string | undefined>(undefined);
  const [addingConsent, setAddingConsent] = useState<boolean>(false);
  const [removingConsentUuid, setRemovingConsentUuid] = useState<string | undefined>(undefined);

  const [error, setError] = useState<string | undefined>(undefined);

  const consentStates = useMemo(() => {
    if (!selectedAppUUID) return [];
    return ConsentStatesByAppUUID[selectedAppUUID] ?? [];
  }, [ConsentStatesByAppUUID, selectedAppUUID]);

  const consentsToGive = useMemo(
    () => consentStates.filter((consentState) => consentState.given !== true),
    [consentStates],
  );

  const givenConsents = useMemo(
    () => consentStates.filter((consentState) => consentState.given === true),
    [consentStates],
  );

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      if (!selectedAppUUID) {
        setError(undefined);
        setLoadingConsents(false);
        return;
      }

      if (isDataSubject && !current_home_uuid) {
        setError(undefined);
        setLoadingConsents(false);
        return;
      }

      setLoadingConsents(true);
      setError(undefined);

      try {
        await loadConsents(selectedAppUUID, false);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unexpected Error");
        }
      } finally {
        if (!cancelled) {
          setLoadingConsents(false);
        }
      }
    };

    void run();

    return () => {
      cancelled = true;
    };
  }, [selectedAppUUID, isDataSubject, current_home_uuid, loadConsents]);

  const onAcceptAllConsents = async () => {
    if (!current_home_uuid) {
      setError("No home selected.");
      return;
    }
    if (!selectedAppUUID) {
      setError("No application selected.");
      return;
    }
    if (consentsToGive.length === 0) return;

    setAcceptingAllConsents(true);
    setError(undefined);

    try {
      const consentUUIDsToGive = consentsToGive.map(
        (consentState) => consentState.uuid,
      );
      await giveConsentsInSmartHome(current_home_uuid, selectedAppUUID, consentUUIDsToGive);
      await loadConsents(selectedAppUUID, true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected Error");
    } finally {
      setAcceptingAllConsents(false);
    }
  };

  const onGiveSingleConsent = async (consentUuid: string) => {
    if (!current_home_uuid) {
      setError("No home selected.");
      return;
    }
    if (!selectedAppUUID) {
      setError("No application selected.");
      return;
    }

    const alreadyGiven = consentStates.some(
      (consentState) => consentState.uuid === consentUuid && consentState.given === true,
    );
    if (alreadyGiven) return;

    setGivingConsentUuid(consentUuid);
    setError(undefined);

    try {
      await giveConsentsInSmartHome(current_home_uuid, selectedAppUUID, [consentUuid]);
      await loadConsents(selectedAppUUID, true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected Error");
    } finally {
      setGivingConsentUuid(undefined);
    }
  };

  const onWithdrawSingleConsent = (consentUuid: string) => {
    if (!onWithdrawConsents) return;
    if (!current_home_uuid) {
      setError("No home selected.");
      return;
    }
    if (!selectedAppUUID) {
      setError("No application selected.");
      return;
    }

    setError(undefined);
    onWithdrawConsents([consentUuid]);
  };

  const onWithdrawAllConsents = () => {
    if (!onWithdrawConsents) return;
    if (!current_home_uuid) {
      setError("No home selected.");
      return;
    }
    if (!selectedAppUUID) {
      setError("No application selected.");
      return;
    }

    const consentUUIDsToWithdraw = givenConsents.map((consentState) => consentState.uuid);
    if (consentUUIDsToWithdraw.length === 0) return;

    setError(undefined);
    onWithdrawConsents(consentUUIDsToWithdraw);
  };

  const onAddConsent = async () => {
    if (!selectedAppUUID) return;

    const normalizedConsent = consentInput.trim();
    if (!normalizedConsent) {
      setError("Insert a consent content.");
      return;
    }

    setAddingConsent(true);
    setError(undefined);

    try {
      await addAvailableConsentToManagedApplication(selectedAppUUID, normalizedConsent);
      await loadConsents(selectedAppUUID, true);
      setConsentInput("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected Error");
    } finally {
      setAddingConsent(false);
    }
  };

  const onRemoveConsent = async (consentUuid: string) => {
    if (!selectedAppUUID) return;

    setRemovingConsentUuid(consentUuid);
    setError(undefined);

    try {
      await removeAvailableConsentFromManagedApplication(selectedAppUUID, consentUuid);
      await loadConsents(selectedAppUUID, true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected Error");
    } finally {
      setRemovingConsentUuid(undefined);
    }
  };

  return (
    <>
      <Card className="h-100 p-0">
        <Card.Body>
          <Row className="align-items-center g-2 mb-2">
            <Col>
              <strong>Consents</strong>
            </Col>

            {isDataSubject ? (
              <Col xs="auto" className="d-inline-flex gap-2">
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={onAcceptAllConsents}
                  disabled={loadingConsents || acceptingAllConsents || !!givingConsentUuid || consentsToGive.length === 0 || !current_home_uuid}
                >
                  {acceptingAllConsents ? (
                    <span className="d-inline-flex align-items-center gap-2">
                      <Spinner animation="border" size="sm" />
                      Accepting…
                    </span>
                  ) : (
                    "Accept all"
                  )}
                </Button>
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={onWithdrawAllConsents}
                  disabled={loadingConsents || acceptingAllConsents || !!givingConsentUuid || givenConsents.length === 0 || !current_home_uuid || !onWithdrawConsents}
                >
                  Revoke all
                </Button>
              </Col>
            ) : undefined}

            {isManagerRole && !((selectedApp?.name ?? "").toLowerCase().includes("com.smartotum")) ? (
              <Col xs="auto">
                <Button
                  className="circular-button me-0"
                  style={{ color: "#181d1f" }}
                  disabled={loadingConsents || addingConsent || !!removingConsentUuid}
                  onClick={() => {
                    setError(undefined);
                    setConsentInput("");
                    setShowManageConsentsModal(true);
                  }}
                  title="Manage consents"
                  aria-label="Manage consents"
                >
                  <i className="fa-solid fa-pencil" style={{ fontSize: "0.90rem" }}></i>
                </Button>
              </Col>
            ) : undefined}
          </Row>

          {error ? (
            <Row className="mb-2">
              <Col className="text-danger">{error}</Col>
            </Row>
          ) : undefined}

          {loadingConsents ? (
            <Row>
              <Col className="d-inline-flex align-items-center gap-2 text-muted">
                <Spinner animation="border" size="sm" />
                Loading consents…
              </Col>
            </Row>
          ) : consentStates.length > 0 ? (
            <Row className="g-2">
              {isDataSubject ? (
                consentStates.map((consentState) => {
                  const consent = consentState;
                  const isGiven = consentState.given === true;
                  return (
                    <Col xs={12} key={consent.uuid}>
                      <div className="d-inline-flex align-items-center gap-2 border rounded-pill ps-3 pe-2 py-1 mb-1">
                        <span>{consent.content}</span>
                        <Button
                          variant="link"
                          className="p-0 d-inline-flex align-items-center"
                          onClick={() => {
                            if (isGiven) {
                              onWithdrawSingleConsent(consent.uuid);
                            } else {
                              void onGiveSingleConsent(consent.uuid);
                            }
                          }}
                          disabled={loadingConsents || acceptingAllConsents || !!givingConsentUuid || !current_home_uuid || (isGiven && !onWithdrawConsents)}
                        >
                          {givingConsentUuid === consent.uuid ? (
                            <Spinner animation="border" size="sm" />
                          ) : isGiven ? (
                            <CheckCircleFill className="text-success" aria-label="revoke consent" title="Revoke" />
                          ) : (
                            <Circle className="text-muted" aria-label="give consent" title="Give" />
                          )}
                        </Button>
                      </div>
                    </Col>
                  );
                })
              ) : (
                consentStates.map((consentState) => (
                  <Col xs={12} key={consentState.uuid}>
                    <div className="d-inline-flex align-items-center border rounded-pill px-3 py-1 mb-1">
                      <span>{consentState.content}</span>
                    </div>
                  </Col>
                ))
              )}
            </Row>
          ) : (
            <Row>
              <Col className="text-muted">No available consents for this app.</Col>
            </Row>
          )}
        </Card.Body>
      </Card>

      {isManagerRole && !((selectedApp?.name ?? "").toLowerCase().includes("com.smartotum")) ? (
        <Modal show={showManageConsentsModal} onHide={() => setShowManageConsentsModal(false)} centered>
          <Modal.Header closeButton>
            <Modal.Title>Manage Consents</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Row className="g-3">
              <Col xs={12}>
                <div className="small fw-semibold">Current consents</div>
              </Col>

              {consentStates.length === 0 ? (
                <Col xs={12}>
                  <div className="text-muted small">No consents configured.</div>
                </Col>
              ) : (
                <Col xs={12}>
                  <Row className="g-2">
                    {consentStates.map((consentState) => {
                      const consent = consentState;
                      return (
                        <Col xs={12} key={consent.uuid}>
                          <div className="d-inline-flex align-items-center gap-2 border rounded-pill py-1 px-3 mb-1">
                            <span className="text-nowrap">{consent.content}</span>
                            <Button
                              size="sm"
                              variant="link"
                              className="text-danger p-0 d-inline-flex align-items-center"
                              style={{ lineHeight: 1 }}
                              disabled={addingConsent || !!removingConsentUuid}
                              onClick={() => onRemoveConsent(consent.uuid)}
                              aria-label={`Remove ${consent.content}`}
                            >
                              {removingConsentUuid === consent.uuid ? (
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
                      );
                    })}
                  </Row>
                </Col>
              )}

              <Col xs={12}>
                <Row className="g-2 align-items-start">
                  <Col xs={12} md>
                    <Form.Group className="mb-0">
                      <Form.Control
                        type="text"
                        value={consentInput}
                        onChange={(e) => setConsentInput(e.target.value)}
                        placeholder="Consent content"
                        disabled={addingConsent || !!removingConsentUuid}
                      />
                    </Form.Group>
                  </Col>
                  <Col xs="auto">
                    <Button variant="primary" onClick={onAddConsent} disabled={addingConsent || !!removingConsentUuid || consentInput.trim() === ""}>
                      {addingConsent ? (
                        <span className="d-inline-flex align-items-center gap-2">
                          <Spinner animation="border" size="sm" />
                          Adding…
                        </span>
                      ) : "Add"}
                    </Button>
                  </Col>
                </Row>
              </Col>

              {error ? (
                <Col xs={12}>
                  <div className="text-danger small">{error}</div>
                </Col>
              ) : undefined}
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button
              variant="outline-secondary"
              onClick={() => setShowManageConsentsModal(false)}
              disabled={addingConsent || !!removingConsentUuid}
            >
              Close
            </Button>
          </Modal.Footer>
        </Modal>
      ) : undefined}
    </>
  );
}

export { AppConsentsPanel };
