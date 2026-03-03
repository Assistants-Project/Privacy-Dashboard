import { useMemo } from "react";
import { Col, Container, Row } from "react-bootstrap";
import { useAuth } from "../contexts/AuthContext";
import { useApp } from "../contexts/AppsContext";
import { HomeSelector } from "../components/Home/HomeSelector";
import { AppsOverviewPanel } from "../components/Home/AppsOverviewPanel";
import { DocumentStatus } from "../models/app";

function Home() {
  const { user, isDataSubject } = useAuth();
  const { apps } = useApp();
  const sectionStyle = { backgroundColor: "#f8f9fa" };
  const allApps = apps ?? [];

  const hasAppsNeedingAttention = useMemo(() => {
    if (isDataSubject) {
      return allApps.some((app) => (app.pending_right_requests_count ?? 0) > 0);
    }

    return allApps.some(
      (app) =>
        app.pn_status === DocumentStatus.Missing ||
        app.pia_status === DocumentStatus.Missing ||
        !app.evaluation ||
        (app.pending_right_requests_count ?? 0) > 0,
    );
  }, [allApps, isDataSubject]);

  return (
    <Container className="py-1 h-100 d-flex flex-column" style={{ minHeight: 0 }}>
      <Row className="mb-3">
        <Col className="text-center">
          <h3 className="display-5 mb-1">Welcome</h3>
          {user ? (
            <h2 className="mb-0">{user.firstname} {user.lastname}</h2>
          ) : undefined}
        </Col>
      </Row>
      {isDataSubject ? (
        <Row className="mb-3 flex-shrink-0">
          <Col>
            <Container fluid className={`border rounded-3 p-3 overflow-hidden`} style={sectionStyle}>
              <HomeSelector />
            </Container>
          </Col>
        </Row>
      ) : undefined}
      <Row>
        <Col>
          <Container
            fluid
            className="border rounded-3 p-3 d-flex flex-column"
            style={sectionStyle}
          >
            <AppsOverviewPanel />
          </Container>
        </Col>
      </Row>
    </Container>
  );
}

export { Home };
