import { Card, Col, Container, Row } from "react-bootstrap";
import { useCallback, useEffect, useState } from "react";
import { DocumentStatus } from "../../models/app";
import { useApp } from "../../contexts/AppsContext";
import { AppsList } from "../../components/Apps/AppsList";
import { PrivacyNoticeEditor } from "../../components/PrivacyNotice/PrivacyNoticeEditor";

function PrivacyNotice() {
  const { loadingApps, setSelectedAppUUID, selectedAppUUID, selectedApp, managedApps } = useApp();
  const [panelExpanded,setPanelExpanded,] = useState(true);

  const closePanel = useCallback(() => {
    setSelectedAppUUID(undefined);
  }, [setSelectedAppUUID,]);

  //serve per deselezionare selected app uuid se non è managed cosi da non mostrarla nella pagina PN
  useEffect(() => {
    if (loadingApps) return;
    if (!selectedAppUUID) return;
    const isManaged = selectedApp?.pn_status === DocumentStatus.Forbidden;
    if (isManaged) setSelectedAppUUID(undefined);
  }, [loadingApps, managedApps, selectedAppUUID, setSelectedAppUUID,]);

  return (
    <Container fluid className="py-2 d-flex flex-column overflow-hidden h-100" style={{ minHeight: 0 }}>
      <Row className="mb-3 flex-shrink-0">
        <Col>
          <h1 className="mb-0">
            Privacy Notice
          </h1>
        </Col>
      </Row>
      <Row className="g-3 flex-grow-1 overflow-hidden" style={{ minHeight: 0 }}>
        <Col xs={3} lg={4} className="d-flex flex-column overflow-hidden" style={{ minHeight: 0 }}>
          <AppsList closePanel={closePanel} getDocumentStatus={(app) => app.pn_status} />
        </Col>

        <Col xs={9} lg={8} className="d-flex flex-column overflow-hidden" style={{ minHeight: 0 }}>
          {!selectedApp ? (
            <Card className="p-0">
              <Card.Body className="text-muted">
                Select an app to see the PN.
              </Card.Body>
            </Card>
	          ) : (
	            <Card className={panelExpanded ? "p-0 overflow-hidden d-flex flex-column flex-grow-1" : "p-0"} style={panelExpanded ? { minHeight: 0 } : undefined}>
	              <Card.Body className={panelExpanded ? "d-flex flex-column flex-grow-1 gap-3 overflow-hidden" : "d-flex flex-column gap-3"} style={panelExpanded ? { minHeight: 0 } : undefined}>
	                <PrivacyNoticeEditor closePanel={closePanel} setPanelExpanded={setPanelExpanded} />
	              </Card.Body>
	            </Card>
	          )}
	        </Col>
      </Row>
    </Container>
  );
}

export { PrivacyNotice };
