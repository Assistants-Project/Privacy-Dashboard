import { Card, Col, Container, Row } from "react-bootstrap";
import { useCallback, useEffect, useState } from "react";
import { useApp } from "../../contexts/AppsContext";
import { AppsList } from "../../components/Apps/AppsList";
import { AppModel, DocumentStatus } from "../../models/app";
import { QuestionnaireEditor } from "../../components/Questionnaire/QuestionnaireEditor";

function Questionnaire() {
  const {
    loadingApps,
    setSelectedAppUUID,
    selectedAppUUID,
    selectedApp,
    managedApps,
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
    const isManaged = managedApps.some((app) => app.uuid === selectedAppUUID);
    if (!isManaged) setSelectedAppUUID(undefined);
  }, [loadingApps, managedApps, selectedAppUUID, setSelectedAppUUID]);

  const markQuestionnaireAvailable = useCallback((appUUID: string) => {
    setStatusOverrides((prev) => ({
      ...prev,
      [appUUID]: DocumentStatus.Available,
    }));
  }, []);

  const getQuestionnaireStatus = useCallback(
    (app: AppModel): DocumentStatus =>
      statusOverrides[app.uuid] ??
      (app.evaluation ? DocumentStatus.Available : DocumentStatus.Missing),
    [statusOverrides],
  );

  return (
    <Container
      fluid
      className="py-2 d-flex flex-column overflow-hidden h-100"
      style={{ minHeight: 0 }}
    >
      <Row className="mb-3 flex-shrink-0">
        <Col>
          <h1 className="mb-0">Questionnaire</h1>
        </Col>
      </Row>
      <Row className="g-3 flex-grow-1 overflow-hidden" style={{ minHeight: 0 }}>
        <Col
          xs={3}
          lg={4}
          className="d-flex flex-column overflow-hidden"
          style={{ minHeight: 0 }}
        >
          <AppsList
            closePanel={closePanel}
            getDocumentStatus={getQuestionnaireStatus}
          />
        </Col>

        <Col
          xs={9}
          lg={8}
          className="d-flex flex-column overflow-hidden"
          style={{ minHeight: 0 }}
        >
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
                <QuestionnaireEditor
                  closePanel={closePanel}
                  onQuestionnaireSaved={markQuestionnaireAvailable}
                  questionnaireAvailable={
                    getQuestionnaireStatus(selectedApp) ===
                    DocumentStatus.Available
                  }
                />
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
    </Container>
  );
}

export { Questionnaire };
