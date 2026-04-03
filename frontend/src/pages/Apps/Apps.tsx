import {
  Button, Card, Col, Container, Row,
} from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { useState } from "react";
import { useApp } from "../../contexts/AppsContext";

import { AppCreationPanel } from "../../components/Apps/AppCreationPanel";
import { AppsList } from "../../components/Apps/AppsList";
import { AppDetailsPanel } from "../../components/Apps/AppDetailsPanel";

export function Apps() {

  const { loading, isDataController } = useAuth();
  const { loadingApps, setSelectedAppUUID, errorApps, apps } = useApp();
  const [showCreateAppModal, setShowCreateAppModal] = useState(false);

  const closePanel = () => setSelectedAppUUID(undefined);

  return (
    <Container fluid className="py-2 apps-page" style={{ minHeight: 0 }}>

      {loadingApps ? (
        <Card className="mb-3 p-0 flex-shrink-0">
          <Card.Body>Loading…</Card.Body>
        </Card>
      ) : undefined}

      {errorApps ? (
        <Card bg="danger" text="white" className="mb-3 p-0 flex-shrink-0">
          <Card.Body>{errorApps}</Card.Body>
        </Card>
      ) : undefined}

      {!loading && !loadingApps && !errorApps ? (
        <Row
          className="g-3 align-items-start align-items-lg-stretch apps-page-body">
          <Col xs={12} lg={6} className="apps-list-col" >
            <AppsList closePanel={closePanel} getVote={(app) => app.evaluation ? app.evaluation : "no vote"} dataToRender={apps ?? []} />
          </Col>

          <Col xs={12} lg={6} className="apps-detail-col">

            {isDataController ? (
              <div className="d-flex justify-content-end mb-2">
                <Button
                  className="circular-button me-0"
                  style={{ color: "#181d1f" }}
                  onClick={() => setShowCreateAppModal(true)}
                  aria-label="Create application"
                  title="Create application"
                >
                  <i className="fa-solid fa-plus"></i>
                </Button>
              </div>
            ) : undefined}

            <AppDetailsPanel />
          </Col>
        </Row>
      ) : undefined}

      {isDataController ? (
        <AppCreationPanel
          show={showCreateAppModal}
          onHide={() => setShowCreateAppModal(false)}
        />
      ) : undefined}
    </Container>
  );
}
