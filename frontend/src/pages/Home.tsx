import { Card, Col, Container, Row } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { Role } from "../models/user";
import { DocumentStatus } from "../models/app";
import { useAuth } from "../contexts/AuthContext";
import { HomeSelector } from "../components/HomeSelector";
import { useApp } from "../contexts/AppsContext";

function Home() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const isDataSubject = user?.role === Role.DataSubject;
  const { managedApps, setSelectedAppUUID } = useApp();
  const appsNeedingAttention = managedApps.filter((app) => app.pn_status === DocumentStatus.Missing || app.pia_status === DocumentStatus.Missing || !app.evaluation);

  return (
    <Container className="py-2">
      <Row className="mb-2">
        <Col>
          <h3>Welcome{user ? `, ${user.firstname} ${user.lastname}` : ""}</h3>
        </Col>
      </Row>
      {isDataSubject ? (
        <Row>
          <Col>
            <HomeSelector />
          </Col>
        </Row>
      ) : (
        <>
          <Row className=" pt-2 mb-3">
            <Col>
              <h4 className="mb-0">Apps overview</h4>
            </Col>
          </Row>
          <Row className="mb-3">
            <Col>
              <div className="text-muted">
                Legend: <span className="text-success"> green</span> = document available | <span className="text-danger">red</span> = document missing.
              </div>
            </Col>
          </Row>
          {managedApps.length === 0 ? (
            <Row>
              <Col>
                <Card>
	                  <Card.Body className="text-muted">No managed apps.</Card.Body>
	                </Card>
	              </Col>
	            </Row>
	          ) : (
	            <Row xs={1} md={2} className="g-3">
	              {appsNeedingAttention.map((app) => {


	                const pnAvailable = app.pn_status === DocumentStatus.Available;
	                const piaAvailable = app.pia_status === DocumentStatus.Available;
                  const questionnaireAvailable = !!app.evaluation;

	                return (
	                  <Col key={app.uuid}>
	                    <Card className="h-100 p-0">
	                      <Card.Body>
	                        <Row className="align-items-start justify-content-between">
	                          <Col>
	                            <strong>{app.name}</strong>
	                            {app.description ? <div className="text-muted">{app.description}</div> : <div className="text-muted">(no description)</div>}
	                          </Col>
	                          <Col xs="auto" className="d-flex flex-column align-items-end gap-1">
	                            <button type="button" className={pnAvailable ? "btn p-0 text-end text-success home-doc-link" : "btn p-0 text-end text-danger home-doc-link"} onClick={() => {setSelectedAppUUID(app.uuid);navigate("/privacy-notice");}}>Privacy Notice</button>
	                            <button type="button" className={piaAvailable ? "btn p-0 text-end text-success home-doc-link" : "btn p-0 text-end text-danger home-doc-link"} onClick={() => {setSelectedAppUUID(app.uuid);navigate("/privacy-impact-assessment");}}>Privacy Impact Assessment</button>
	                            <button type="button" className={questionnaireAvailable ? "btn p-0 text-end text-success home-doc-link" : "btn p-0 text-end text-danger home-doc-link"} onClick={() => {setSelectedAppUUID(app.uuid);navigate("/questionnaire");}}>Questionnaire</button>
	                          </Col>
	                        </Row>
	                      </Card.Body>
	                    </Card>
	                  </Col>
	                );
	              })}
	            </Row>
	          )}
        </>
      )}
    </Container>

  );
}

export { Home };
