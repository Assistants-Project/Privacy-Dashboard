import { Badge, Button, Card, CloseButton, Col, Container, Row } from "react-bootstrap";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { useApp } from "../../contexts/AppsContext";
import { DocumentStatus } from "../../models/app";
import { Evaluation } from "../../models/question";
import { SubmitRightRequestModal } from "../Rights/RightRequestSubmitForm";
import { AppAssignmentPanel } from "./AppAssignmentPanel";
import { AppConsentsPanel } from "./AppConsentsPanel";

export function AppDetailsPanel() {
  const { isDataSubject } = useAuth();
  const { selectedApp, setSelectedAppUUID, ConsentStatesByAppUUID } = useApp();
  const [showSubmitRightModal, setShowSubmitRightModal] = useState(false);

  const closePanel = () => setSelectedAppUUID(undefined);

  const PNmissing = selectedApp?.pn_status === DocumentStatus.Missing;
  const PIAmissing = selectedApp?.pia_status === DocumentStatus.Missing;

  const questionnaireMissing = !selectedApp?.evaluation;
  const pendingRightRequestsCount = selectedApp?.pending_right_requests_count ?? 0;
  const hasPendingRightRequests = pendingRightRequestsCount > 0;
  const rightRequestsButtonVariant = hasPendingRightRequests? "outline-danger": "outline-success";
  const rightRequestsLabel = hasPendingRightRequests? `Pending Right Requests (${pendingRightRequestsCount})`: "Right Requests";
  const rightRequestsTarget = selectedApp? `/rights?app=${encodeURIComponent(selectedApp.name)}${hasPendingRightRequests ? "&status=PENDING" : ""}`: "/rights";
  const rightRequestsLinkClass = ["btn btn-sm border-2", rightRequestsButtonVariant === "outline-danger" ? "btn-outline-danger" : "btn-outline-success"].join(" ");
  const consentsLoadedForSelectedApp = selectedApp?.uuid ? ConsentStatesByAppUUID[selectedApp.uuid] !== undefined : false;

  return (
    <>
      <Card className="p-0 sticky-top z-1" style={{ top: "1rem" }}>
        <Card.Body className="d-flex flex-column gap-3">
          {!selectedApp ? (
            <div className="text-muted">
              Select an app to see details.
            </div>
          ) : (
            <>
              <Container fluid className="d-flex px-0 justify-content-between align-items-start">
                <Container fluid className="ps-0">
                  <h3>
                    {selectedApp.title}
                    <span className="text-muted fw-normal fs-6 ms-2">| {selectedApp.name}</span>
                  </h3>
                  <div className="text-muted">
                    <span>Vote:&nbsp;</span>
                    {selectedApp.evaluation ? <Badge bg={evaluationBadge(selectedApp.evaluation)}>{selectedApp.evaluation}</Badge> : "—"}
                  </div>
                </Container>
                <CloseButton onClick={closePanel} />
              </Container>

              {selectedApp.description ? (
                <div className="text-muted">
                  {selectedApp.description}
                </div>
              ) : undefined}

              <Container fluid className="d-flex flex-wrap gap-2 ps-0">
                <Link className={["btn btn-sm border-2", PNmissing ? "btn-outline-danger" : "btn-outline-success"].join(" ")} to="/privacy-notice">
                  Privacy Notice
                </Link>
                {!isDataSubject ? (
                  <Link
                    className={[
                      "btn btn-sm border-2",
                      questionnaireMissing
                        ? "btn-outline-danger"
                        : "btn-outline-success",
                    ].join(" ")}
                    to="/questionnaire"
                  >
                    Questionnaire
                  </Link>
                ) : undefined}
                {!isDataSubject ? (
                  <Link className={["btn btn-sm border-2", PIAmissing ? "btn-outline-danger" : "btn-outline-success"].join(" ")} to="/privacy-impact-assessment">
                    Privacy Impact Assessment
                  </Link>
                ) : undefined}
                <Link className={rightRequestsLinkClass} to={rightRequestsTarget}>
                  {rightRequestsLabel}
                </Link>
              </Container>

              <AppAssignmentPanel />

              {isDataSubject ? (
                <Row>
                  <Col>
                    <Card className="h-100 p-0">
                      <Card.Body>
                        <Row className="g-3">
                          <Col xs={12}>
                            <strong>Actions</strong>
                          </Col>
                          <Col xs={12}>
                            <Button
                              variant="outline-primary"
                              size="sm"
                              onClick={() => setShowSubmitRightModal(true)}
                              disabled={!consentsLoadedForSelectedApp}
                            >
                              Exercise Rights / Withdraw Consent
                            </Button>
                          </Col>
                        </Row>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>
              ) : undefined}

              <Row>
                <Col>
                  <AppConsentsPanel />
                </Col>
              </Row>

              {selectedApp.questionnaire_summary ? (
                <Card className="p-0">
                  <Card.Body>
                    <strong>Questionnaire summary</strong>
                    <div className="mt-2 text-muted">
                      {selectedApp.questionnaire_summary}
                    </div>
                  </Card.Body>
                </Card>
              ) : undefined}

              {isDataSubject && selectedApp.installed_at ? (
                <div className="text-muted">
                  Installed at: {selectedApp.installed_at}
                </div>
              ) : undefined}
            </>
          )}
        </Card.Body>
      </Card>

      {isDataSubject && selectedApp ? (
        <SubmitRightRequestModal show={showSubmitRightModal} onHide={() => setShowSubmitRightModal(false)} />
      ) : undefined}
    </>
  );
}

function evaluationBadge(evaluation: Evaluation) {
  switch (evaluation) {
    case Evaluation.GREEN:
      return "success";
    case Evaluation.ORANGE:
      return "warning";
    case Evaluation.RED:
      return "danger";
    default:
      return "secondary";
  }
}
