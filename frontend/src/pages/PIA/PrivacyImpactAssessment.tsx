import { Card, Col, Container, Row } from "react-bootstrap";
import { useCallback, useEffect } from "react";
import { useApp } from "../../contexts/AppsContext";
import { DocumentStatus } from "../../models/app";
import { AppsList } from "../../components/Apps/AppsList";
import { PrivacyImpactAssessmentEditor } from "../../components/PIA/PrivacyImpactAssessmentEditor";

function PrivacyImpactAssessment() {
   const { loadingApps, setSelectedAppUUID, selectedAppUUID, selectedApp, managedApps } = useApp();

  const closePanel = useCallback(() => {
    setSelectedAppUUID(undefined);
  }, [setSelectedAppUUID,]);

  //serve per deselezionare selected app uuid se non è managed cosi da non mostrarla nella pagina PN
  useEffect(() => {
    if (loadingApps) return;
    if (!selectedAppUUID) return;
    const isManaged = selectedApp?.pia_status === DocumentStatus.Forbidden;
    if (isManaged) setSelectedAppUUID(undefined);
  }, [loadingApps, managedApps, selectedAppUUID, setSelectedAppUUID,]);

  return (
    <Container fluid className="mx-auto py-2 d-flex flex-column overflow-hidden h-100" style={{ minHeight: 0 }}>
      <Row className="mb-3 flex-shrink-0">
        <Col>
          <h1 className="mb-0">
            Privacy Impact Assessment
          </h1>
        </Col>
      </Row>
      <Row className="g-3 flex-grow-1 overflow-hidden" style={{ minHeight: 0 }}>
        <Col xs={3} lg={4} className="d-flex flex-column overflow-hidden" style={{ minHeight: 0 }}>
          <AppsList closePanel={closePanel} getDocumentStatus={(app) => app.pia_status} />
        </Col>

        <Col xs={9} lg={8} className="d-flex flex-column overflow-hidden" style={{ minHeight: 0 }}>
          {!selectedApp ? (
            <Card className="p-0">
              <Card.Body className="text-muted">
                Select an app to see the PIA.
              </Card.Body>
            </Card>
          ) : (
            <Card className="p-0 overflow-hidden d-flex flex-column flex-grow-1" style={{ minHeight: 0 }}>
              <Card.Body className="d-flex flex-column flex-grow-1 gap-3 overflow-hidden" style={{ minHeight: 0 }}>
                <PrivacyImpactAssessmentEditor closePanel={closePanel} />
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
    </Container>
  );
}

export { PrivacyImpactAssessment };
