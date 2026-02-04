import {
  Badge, Button, Card, CloseButton, Col, Container, Form, Row,
} from "react-bootstrap";
import { useAuth } from "../../components/Authentication/AuthContext";
import { Role, User } from "../../models/user";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../../components/AppsContext";

import { AppAssignmentPanel } from "../../components/AppAssignmentPanel";
import { DocumentStatus } from "../../models/app"
import { SubmitRightRequestModal } from "../../components/Rights/RightRequestSubmitForm";

export function Apps() {

  const { user, loading } = useAuth();
  const {loadingApps,selectedApp,setSelectedAppUUID,selectedAppUUID,errorApps,apps} = useApp();

  const [query, setQuery] = useState("");
  const [showSubmitRightModal, setShowSubmitRightModal] = useState(false);

  const isDataSubject = user?.role === Role.DataSubject;
  const isDataController = user?.role === Role.DatController;

  const closePanel = () => setSelectedAppUUID(undefined);

  //direttamente dal flag pn_status possiamo decidere se disponibile, mancante o non di nostra competenza
  const PNavailable = selectedApp?.pn_status === DocumentStatus.Available;
  const PNmissing = selectedApp?.pn_status === DocumentStatus.Missing;
  const PNforbidden = selectedApp?.pn_status === DocumentStatus.Forbidden;

  //stessa cosa per vedere lo stato del PIA
  const PIAavailable = selectedApp?.pia_status === DocumentStatus.Available;
  const PIAmissing = selectedApp?.pia_status === DocumentStatus.Missing;
  const PIAforbidden = selectedApp?.pia_status === DocumentStatus.Forbidden;




  return (
    <Container className="py-3">
      <Row className="mb-3">
        <Col>
          <h1 className="mb-0">
            {isDataSubject ? "Installed Apps" : "Catalog Apps"}
          </h1>
        </Col>
      </Row>

      {loadingApps ? (
        <Card className="mb-3 p-0">
          <Card.Body>Loading…</Card.Body>
        </Card>
      ) : undefined}

      {errorApps ? (
        <Card bg="danger" text="white" className="mb-3 p-0">
          <Card.Body>{errorApps}</Card.Body>
        </Card>
      ) : undefined}

      {!loading && !loadingApps && !errorApps ? (
        <Row className="g-3 align-items-start">
          <Col xs={12} lg={7}>
            <Container fluid className="d-flex flex-column gap-3">
              <Card className="p-0">
                <Card.Body>
                  <Form.Group controlId="apps-search">
                    <Form.Label className="mb-1">Search</Form.Label>
                    <Form.Control
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="Name, description…"
                    />
                  </Form.Group>
                </Card.Body>
              </Card>

              {apps?.length === 0 ? (
                <Card className="p-0">
                  <Card.Body className="text-muted">No apps.</Card.Body>
                </Card>
              ) : (
                <Row xs={1} md={2} className="g-4">
                  {apps
                    ?.filter(
                      (app) =>
                        app.name.includes(query) ||
                        app.description?.includes(query),
                    )
                    .map((app) => {
                      const selected = app.uuid === selectedAppUUID;

                      const title =
                        app.name && app.name.trim() !== ""
                          ? app.name
                          : "Nome non impostato";
                      const vote = app.evaluation ? app.evaluation : "no vote";
                      const description = app.description;

                      return (
                        <Col key={app.uuid}>
                          <Card
                            role="button"
                            tabIndex={0}
                            onClick={() => {
                              if (selected) {
                                closePanel();
                                return;
                              }
                              setSelectedAppUUID(app.uuid);
                            }}
                            className={[
                              "h-100 p-0 apps_card_hover",
                              selected ? "border-3 apps_card_selected" : "",
                            ].join(" ")}
                            style={{ cursor: "pointer" }}
                          >
                            <Card.Body>
                              <div className="d-flex align-items-baseline gap-2">
                                <strong>{title}</strong>
                                <span className="text-muted">({vote})</span>
                              </div>
                              {description ? (
                                <div className="text-muted">{description}</div>
                              ) : (
                                <div className="text-muted">
                                  (no description)
                                </div>
                              )}
                            </Card.Body>
                          </Card>
                        </Col>
                      );
                    })}
                </Row>
              )}
            </Container>
          </Col>

          <Col xs={12} lg={5}>
            <Card className="sticky-top z-1 p-0" style={{ top: "1rem" }}>
              <Card.Body className="d-flex flex-column gap-3">
                {!selectedApp ? (
                  <div className="text-muted">
                    Select an app to see details.
                  </div>
                ) : (
                  <>
                    <Container
                      fluid
                      className="d-flex justify-content-between align-items-start"
                    >
                      <Container fluid className="ps-0">
                        <h2 className="h4 mb-1">
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
                        className="btn btn-outline-primary btn-sm"
                        to="/rights"
                      >
                        {isDataSubject ? "Rights" : "Requests"}
                      </Link>
                      {isDataSubject ? (
                        <Button
                          variant="outline-primary"
                          size="sm"
                          onClick={() => setShowSubmitRightModal(true)}
                        >
                          Exercise a right
                        </Button>
                      ) : undefined}
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
                      <Link
                        className="btn btn-outline-secondary btn-sm"
                        to="/questionnaire"
                      >
                        Questionnaire
                      </Link>
                      <Link
                        className={[
                          "btn btn-sm border-2",
                          PIAforbidden ? "btn-outline-secondary disabled"
                            : PIAmissing ? "btn-outline-danger"
                              : "btn-outline-success"
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
                      {isDataController && selectedApp ? (
                        <AppAssignmentPanel />
                      ) : undefined}
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
    </Container>
  );
}
