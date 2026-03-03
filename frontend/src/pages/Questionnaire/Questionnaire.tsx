import { Card, Col, Container, Row } from "react-bootstrap";
import { useCallback, useEffect, useState } from "react";
import { useApp } from "../../contexts/AppsContext";
import { AppsList } from "../../components/Apps/AppsList";
import { AppModel, DocumentStatus } from "../../models/app";
import { QuestionnaireEditor } from "../../components/Questionnaire/QuestionnaireEditor";

function Questionnaire() {
  const {
    loadingApps,
    apps,
    setSelectedAppUUID,
    selectedAppUUID,
    selectedApp,
  } = useApp();

  const [statusOverrides, setStatusOverrides] = useState<
    Record<string, DocumentStatus>
  >({});

  const closePanel = useCallback(() => {
    setSelectedAppUUID(undefined);
  }, [setSelectedAppUUID]);

  // Clear selection if the current app isn't managed (e.g. selection comes from Catalog).
  useEffect(() => {
    if (loadingApps) return;
    if (!selectedAppUUID) return;
    const isManaged = (apps ?? []).some((app) => app.uuid === selectedAppUUID);
    if (!isManaged) setSelectedAppUUID(undefined);
  }, [loadingApps, apps, selectedAppUUID, setSelectedAppUUID]);

  return (
    <Container fluid className="py-2 d-flex flex-column overflow-hidden h-100" style={{ minHeight: 0 }} >
      <Row className="g-3 flex-grow-1 overflow-hidden" style={{ minHeight: 0 }}>
        <Col xs={2} lg={3} className="d-flex flex-column overflow-hidden pe-0 ps-0" style={{ minHeight: 0 }}>
          <AppsList
            closePanel={closePanel}
            getDocumentStatus={(app) =>
              app.evaluation ? DocumentStatus.Available : DocumentStatus.Missing
            }
          />
        </Col>

        <Col xs={10} lg={9} className="d-flex flex-column overflow-hidden ps-0 pe-0" style={{ minHeight: 0 }}>
          {!selectedApp ? (
            <Card className="p-0">
              <Card.Body className="text-muted">
                Select an app to see the Questionnaire.
              </Card.Body>
            </Card>
          ) : (
            <Card
              className="p-0 overflow-hidden d-flex flex-column flex-grow-1"
              style={{ minHeight: 0 }}
            >
              <Card.Body
                id="questionnaire-container"
                className="d-flex flex-column flex-grow-1 gap-3 overflow-hidden"
                style={{ minHeight: 0 }}
              >
                <QuestionnaireEditor closePanel={closePanel} />
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
    </Container>
  );
}

export { Questionnaire };
