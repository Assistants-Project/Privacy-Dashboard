import { useCallback, useEffect, useMemo, useState } from "react";
import { Button, Card, Col, Row, Spinner } from "react-bootstrap";
import { CheckCircleFill, Circle } from "react-bootstrap-icons";
import { useHome } from "../../contexts/HomeContext";
import { AvailableConsentModel } from "../../models/available_consent";
import { fetchAvailableConsentsByApplication, fetchGivenConsentsBySmartHome, giveConsentsInSmartHome, } from "../../services/AvailableConsentService";
import { useApp } from "../../contexts/AppsContext";



function AppConsentsPanel() {

  const { current_home_uuid } = useHome();
  const [loadingConsents, setLoadingConsents] = useState<boolean>(false);
  const [acceptingAllConsents, setAcceptingAllConsents] = useState<boolean>(false);
  const [givingConsentUuid, setGivingConsentUuid] = useState<string | undefined>(undefined);
  const [availableConsents, setAvailableConsents] = useState<AvailableConsentModel[]>([]);
  const [givenConsentUUIDs, setGivenConsentUUIDs] = useState<string[]>([]);
  const [error, setError] = useState<string | undefined>(undefined);
  const {selectedAppUUID} = useApp();

  const givenConsentSet = useMemo(
    () => new Set(givenConsentUUIDs),
    [givenConsentUUIDs],
  );

  //per adesso filtriamo ma sarebbe comodo avere un endpoint dedicato
  const consentsToGive = useMemo(
    () => availableConsents.filter((consent) => !givenConsentSet.has(consent.uuid)),
    [availableConsents, givenConsentSet],
  );

  const loadConsents = useCallback(async () => {

    if (!current_home_uuid || !selectedAppUUID) {
      setAvailableConsents([]);
      setGivenConsentUUIDs([]);
      setError(undefined);
      return;
    }

    setLoadingConsents(true);
    setError(undefined);

    try {

      const [appAvailableConsents, homeGivenConsents] = await Promise.all([
        fetchAvailableConsentsByApplication(selectedAppUUID),
        fetchGivenConsentsBySmartHome(current_home_uuid),
      ]);
      const normalizedAvailableConsents = appAvailableConsents ?? [];

      //sarebbe meglio creare un endpoint per trovare anche i consensi già dati per applicazione e non filtrare da quelli 
      //per la casa
      const normalizedGivenConsentUUIDs = (homeGivenConsents ?? [])
        .filter((givenConsent) => givenConsent.application_uuid === selectedAppUUID)
        .map((givenConsent) => givenConsent.available_consent.uuid);

      setAvailableConsents(normalizedAvailableConsents);
      setGivenConsentUUIDs(Array.from(new Set(normalizedGivenConsentUUIDs)));

    } catch (err) {

      setAvailableConsents([]);
      setGivenConsentUUIDs([]);

      setError(err instanceof Error ? err.message : "Errore inatteso");

    } finally {

      setLoadingConsents(false);

    }
  }, [selectedAppUUID, current_home_uuid]);

  useEffect(() => {
    void loadConsents();
  }, [loadConsents]);

  const onAcceptAllConsents = async () => {

    if (!current_home_uuid) {
      setError("No home selected.");
      return;
    }

    if (consentsToGive.length === 0) return;

    setAcceptingAllConsents(true);
    setError(undefined);

    try {
      await giveConsentsInSmartHome(current_home_uuid, consentsToGive.map((consent) => consent.uuid));

      setGivenConsentUUIDs((prev) => Array.from(new Set([...prev, ...consentsToGive.map((consent) => consent.uuid)])));

    } catch (err) {

      setError(err instanceof Error ? err.message : "Errore inatteso");

    } finally {
      setAcceptingAllConsents(false);
    }
  };

  const onGiveSingleConsent = async (consentUuid: string) => {
    if (!current_home_uuid) {
      setError("No home selected.");
      return;
    }

    if (givenConsentSet.has(consentUuid)) return;

    setGivingConsentUuid(consentUuid);
    setError(undefined);

    try {
      await giveConsentsInSmartHome(current_home_uuid, [consentUuid]);
      setGivenConsentUUIDs((prev) => Array.from(new Set([...prev, consentUuid])));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Errore inatteso");
    } finally {
      setGivingConsentUuid(undefined);
    }
  };

  return (
    <Card className="h-100 p-0">
      <Card.Body>
        <Row className="align-items-center g-2 mb-2">
          <Col>
            <strong>Consents</strong>
          </Col>
          <Col xs="auto">
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
          </Col>
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
        ) : availableConsents.length > 0 ? (
          <Row className="g-2">
            {availableConsents.map((consent) => {
              const isGiven = givenConsentSet.has(consent.uuid);
              return (
                <Col xs="auto" key={consent.uuid}>
                  <Row className="align-items-center border rounded ms-0">
                    <Col>{consent.content}</Col>
                    <Col xs="auto">
                      <Button
                        variant="link" onClick={() => void onGiveSingleConsent(consent.uuid)} disabled={loadingConsents || acceptingAllConsents || !!givingConsentUuid || !current_home_uuid || isGiven}>
                        {givingConsentUuid === consent.uuid ? (
                          <Spinner animation="border" size="sm" />
                        ) :
                          isGiven ? (
                            <CheckCircleFill
                              className="text-success"
                              aria-label="consent given"
                              title="Given"
                            />
                          ) : (
                            <Circle
                              className="text-muted"
                              aria-label="consent not given"
                              title="Not given"
                            />
                          )}
                      </Button>

                    </Col>
                  </Row>
                </Col>
              );
            })}
          </Row>
        ) : (
          <Row>
            <Col className="text-muted">No available consents for this app.</Col>
          </Row>
        )}
      </Card.Body>
    </Card>
  );
}

export { AppConsentsPanel };
