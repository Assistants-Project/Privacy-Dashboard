import {
  Badge, Button, Card, CloseButton, Col, Container, Form, Row,
} from "react-bootstrap";
import { PlusCircle } from "react-bootstrap-icons";
import { useAuth } from "../../contexts/AuthContext";
import { Role, User } from "../../models/user";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useApp } from "../../contexts/AppsContext";

import { AppAssignmentPanel } from "../../components/Apps/AppAssignmentPanel";
import { AppCreationPanel } from "../../components/Apps/AppCreationPanel";
import { DocumentStatus } from "../../models/app"
import { SubmitRightRequestModal } from "../../components/Rights/RightRequestSubmitForm";
import { AppsList } from "../../components/Apps/AppsList";

export function Apps() {

  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const { loadingApps, selectedApp, setSelectedAppUUID, selectedAppUUID, errorApps, apps, managedApps } = useApp();

  const [showSubmitRightModal, setShowSubmitRightModal] = useState(false);
  const [showCreateAppModal, setShowCreateAppModal] = useState(false);

  const isDataSubject = user?.role === Role.DataSubject;
  const isDataController = user?.role === Role.DataController;
  const showQuestionnaire = !isDataSubject;

  const closePanel = () => setSelectedAppUUID(undefined);

  //direttamente dal flag pn_status possiamo decidere se disponibile, mancante o non di nostra competenza
  const PNavailable = selectedApp?.pn_status === DocumentStatus.Available;
  const PNmissing = selectedApp?.pn_status === DocumentStatus.Missing;
  const PNforbidden = selectedApp?.pn_status === DocumentStatus.Forbidden;

  //stessa cosa per vedere lo stato del PIA
  const PIAavailable = selectedApp?.pia_status === DocumentStatus.Available;
  const PIAmissing = selectedApp?.pia_status === DocumentStatus.Missing;
  const PIAforbidden = selectedApp?.pia_status === DocumentStatus.Forbidden;

  const questionnaireForbidden = !showQuestionnaire || !selectedApp || !managedApps.some((app) => app.uuid === selectedApp.uuid);
  const questionnaireMissing = !selectedApp?.evaluation;

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
          <Col xs={12} lg={7} className="apps-list-col" >
            <AppsList closePanel={closePanel} getVote={(app) => app.evaluation ? app.evaluation : "no vote"} dataToRender={apps ?? []}  />
          </Col>

          <Col xs={12} lg={5} className="apps-detail-col">
          
            {isDataController ? (
              <div className="d-flex justify-content-end mb-2">
                <Button
                  variant="link"
                  className="d-inline-flex align-items-center justify-content-center p-0 border-0 bg-transparent text-primary"
                  style={{ width: "34px", height: "34px" }}
                  onClick={() => setShowCreateAppModal(true)}
                  aria-label="Create application"
                  title="Create application"
                >
                  <PlusCircle size={28} />
                </Button>
              </div>
            ) : undefined}

            <Card className="p-0 sticky-top z-1" style={{ top: "1rem" }} >
              <Card.Body className="d-flex flex-column gap-3">
                {!selectedApp ? (
                  <div className="text-muted">
                    Select an app to see details.
                  </div>
                ) : (
                  <>
                    <Container
                      fluid
                      className="d-flex px-0 justify-content-between align-items-start"
                    >
                      <Container fluid className="ps-0">
                        <h2 className="h4">
                          {selectedApp.name && selectedApp.name.trim() !== ""
                            ? selectedApp.name
                            : "Nome non impostato"}
                        </h2>
                        <div className="text-muted">
                          {selectedApp.evaluation
                            ? `Vote: ${selectedApp.evaluation}`
                            : "Vote: —"}
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
	                      <Link
	                        className={[
	                          "btn btn-sm border-2",
                          PNforbidden ? "btn-outline-secondary disabled" //se no disabilitiamo perchè significa che non possiamo leggere il privacy notice
                            : PNmissing ? "btn-outline-danger" //se pn undefined significa che non è mai stato scaricato o tentativo di fetch è fallito
                              : "btn-outline-success"
                        ].join(" ")}
                        to="/privacy-notice"
                        aria-disabled={PNforbidden}
                        onClick={(e) => {
                          //nel caso non sia di nostra competenza il bottone se premuto non porta a nulla
                          if (PNforbidden) {
                            e.preventDefault();
                          }
                        }}
		                      >
		                        Privacy Notice
		                      </Link>
		                      {!isDataSubject && (
		                        <Link
		                          className={[
		                            "btn btn-sm border-2",
		                            questionnaireForbidden
		                              ? "btn-outline-secondary disabled"
		                              : questionnaireMissing
		                                ? "btn-outline-danger"
		                                : "btn-outline-success",
		                          ].join(" ")}
		                          to="/questionnaire"
		                          aria-disabled={questionnaireForbidden}
		                          onClick={(e) => {
		                            if (questionnaireForbidden) {
		                              e.preventDefault();
		                            }
		                          }}
		                        >
		                          Questionnaire
		                        </Link>
		                      )}
		                      {!isDataSubject && (
		                        <Link
		                          className={[
		                            "btn btn-sm border-2",
		                            PIAforbidden
		                              ? "btn-outline-secondary disabled"
		                              : PIAmissing
		                                ? "btn-outline-danger"
		                                : "btn-outline-success",
		                          ].join(" ")}
		                          to="/privacy-impact-assessment"
		                          aria-disabled={PIAforbidden}
		                          onClick={(e) => {
		                            if (PIAforbidden) {
		                              e.preventDefault();
		                            }
		                          }}
		                        >
		                          Privacy Impact Assessment
		                        </Link>
		                      )}
		                    </Container>

                    <Row xs={1} md={2} className="g-3">
                      <Col>
                        <Card className="h-100 p-0">
                          <Card.Body>
                            <strong>Controllers</strong>
                            <div className="mt-2" />
                            {selectedApp.data_controllers?.length ? (
                              <div className="d-flex flex-wrap gap-2">
                                {selectedApp.data_controllers
                                  //gestire caso utente loggato manager dell'App
                                  // .filter((u) => u.email !== user?.email)
                                  .map((contact) => (
                                    <Badge
                                      key={contact.email}
                                      bg="light"
                                      text="dark"
                                      className="border rounded-pill"
                                    >
                                      {`${contact.firstname} ${contact.lastname}`.trim() ||
                                        contact.email}
                                    </Badge>
                                  ))}
                              </div>
                            ) : (
                              <div className="text-muted">Not Assigned</div>
                            )}
                          </Card.Body>
                        </Card>
                      </Col>

                      <Col>
                        <Card className="h-100 p-0">
                          <Card.Body>
                            <strong>DPO</strong>
                            <div className="mt-2" />
                            {selectedApp.dpo ? (
                              <div className="d-flex flex-wrap gap-2">
                                <Badge
                                  bg="light"
                                  text="dark"
                                  className="border rounded-pill"
                                >
                                  {`${selectedApp.dpo.firstname} ${selectedApp.dpo.lastname}`.trim() ||
                                    selectedApp.dpo.email}
                                </Badge>
                              </div>
                            ) : (
                              <div className="text-muted">Not Assigned</div>
                            )}
                          </Card.Body>
                        </Card>
                      </Col>
                    </Row>
                    <Row>
                      <Col>
                        <Card className="h-100 p-0">
                          <Card.Body>
                            <strong>Actions</strong>
                            <div className="mt-2" />
                            {isDataSubject ? (
                              <Button variant="outline-primary" size="sm" onClick={() => setShowSubmitRightModal(true)}>
                                Exercise a right
                              </Button>
                            ) : (
                              <Button variant={(PIAforbidden || PNforbidden) ? "btn-outline-secondary disabled" : "outline-primary"} size="sm" onClick={() => navigate("/rights")}>
                                Manage Rights
                              </Button>
                            )}
                          </Card.Body>
                        </Card>
                      </Col>
                    </Row>

                    <Row>
                      <Col>
                        {isDataController && selectedApp ? (
                          <AppAssignmentPanel />
                        ) : undefined}
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
          </Col>
        </Row>
      ) : undefined}

      {isDataSubject && selectedApp ? (
        <SubmitRightRequestModal
          show={showSubmitRightModal}
          onHide={() => setShowSubmitRightModal(false)}
        />
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
