import { Card, Col, Container, Row } from "react-bootstrap";
import { useCallback } from "react";
import { useApp } from "../../contexts/AppsContext";
import { AppsList } from "../../components/Apps/AppsList";
import { PrivacyImpactAssessmentEditor } from "../../components/PIA/PrivacyImpactAssessmentEditor";

function PrivacyImpactAssessment() {
   const { setSelectedAppUUID, selectedApp } = useApp();

  const closePanel = useCallback(() => {
    setSelectedAppUUID(undefined);
  }, [setSelectedAppUUID,]);

  return (
    <Container fluid className="mx-auto py-2 d-flex flex-column overflow-hidden h-100" style={{ minHeight: 0 }}>
      <Row className="g-3 flex-grow-1 overflow-hidden" style={{ minHeight: 0 }}>
        <Col xs={2} lg={3} className="d-flex flex-column overflow-hidden pe-0 ps-0" style={{ minHeight: 0 }}>
          <AppsList closePanel={closePanel} getDocumentStatus={(app) => app.pia_status} />
        </Col>

        <Col xs={10} lg={9} className="d-flex flex-column overflow-hidden ps-0 ps-0" style={{ minHeight: 0 }}>
          {!selectedApp ? (
            <Card className="p-0">
              <Card.Body className="text-muted">
                Select an app to see the Privacy Impact Assessment.
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
