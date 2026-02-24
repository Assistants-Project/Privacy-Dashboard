import { Col, Container, Row } from "react-bootstrap";
import { useAuth } from "../contexts/AuthContext";
import { HomeSelector } from "../components/Home/HomeSelector";
import { AppsOverviewPanel } from "../components/Home/AppsOverviewPanel";

function Home() {
  const { user, isDataSubject } = useAuth();
  const sectionStyle = { backgroundColor: "#f8f9fa" };

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
      <Row className="flex-grow-1" style={{ minHeight: 0 }}>
        <Col className="d-flex flex-column" style={{ minHeight: 0 }}>
          <Container
            fluid
            className={`border rounded-3 p-3 d-flex h-100 flex-column`}
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
