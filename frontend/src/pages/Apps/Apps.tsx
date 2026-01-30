import { Badge, Card, CloseButton, Col, Container, Form, Row } from "react-bootstrap";
import { useAuth } from "../../components/Authentication/AuthContext";
import { Role } from "../../models/user";

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../../components/AppsContext";

export function Apps() {

  const { user, loading } = useAuth();
  const apps_context = useApp();

  const [query, setQuery] = useState("");
  const [selectedAppUuid, setSelectedAppUuid] = useState<string | undefined>(undefined);

  const selectedApp = apps_context.apps?.find((app) => app.uuid === selectedAppUuid); //comodo per avere sempre la app selezionata
  const isDataSubject = user?.role === Role.DataSubject;

  const closePanel = () => setSelectedAppUuid(undefined);

  return (
    <Container className="py-3">
      <Row className="mb-3">
        <Col>
          <h1 className="mb-0">{isDataSubject? "Installed Apps" : "Catalog Apps"}</h1>
        </Col>
      </Row>

      {apps_context.loadingApps ? (
        <Card className="mb-3 p-0">
          <Card.Body>Loading…</Card.Body>
        </Card>
      ) : undefined}

      {apps_context.errorApps ? (
        <Card bg="danger" text="white" className="mb-3 p-0">
          <Card.Body>{apps_context.errorApps}</Card.Body>
        </Card>
      ) : undefined}

      {!loading && !apps_context.loadingApps && !apps_context.errorApps ? (
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

              {apps_context.apps?.length === 0 ? (
                <Card className="p-0">
                  <Card.Body className="text-muted">No apps.</Card.Body>
                </Card>
              ) : (
                <Row xs={1} md={2} className="g-4">
                  {apps_context.apps
                    ?.filter(
                      (app) =>
                        app.name.includes(query) || app.description?.includes(query),
                    )
                    .map((app) => {
                    const selected = app.uuid === selectedAppUuid;

                    const title =
                      app.name && app.name.trim() !== "" ? app.name : "Nome non impostato";
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
                            setSelectedAppUuid(app.uuid);
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
                              <div className="text-muted">(no description)</div>
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
                  <div className="text-muted">Select an app to see details.</div>
                ) : (
                  <>
                    <Container fluid className="d-flex justify-content-between align-items-start">
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
                      <div className="text-muted">{selectedApp.description}</div>
                    ) : undefined}

                    <Container fluid className="d-flex flex-wrap gap-2 ps-0">
                      <Link className="btn btn-outline-secondary btn-sm" to="/privacy-notice">
                        Privacy Notice
                      </Link>
                      <Link className="btn btn-outline-secondary btn-sm" to="/questionnaire">
                        Questionnaire
                      </Link>
                      <Link
                        className="btn btn-outline-secondary btn-sm"
                        to="/privacy-impact-assessment"
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
                              <div className="text-muted">Not Assiegned</div>
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
                                <Badge bg="light" text="dark" className="border rounded-pill">
                                  {`${selectedApp.dpo.firstname} ${selectedApp.dpo.lastname}`.trim() ||
                                    selectedApp.dpo.email}
                                </Badge>
                              </div>
                            ) : (
                              <div className="text-muted">Not Assiegned</div>
                            )}
                          </Card.Body>
                        </Card>
                      </Col>
                    </Row>

                    {selectedApp.questionnaire_summary ? (
                      <Card className="p-0">
                        <Card.Body>
                          <strong>Questionnaire summary</strong>
                          <div className="mt-2 text-muted">{selectedApp.questionnaire_summary}</div>
                        </Card.Body>
                      </Card>
                    ) : undefined}

                    {isDataSubject && selectedApp.installed_at ? (
                      <div className="text-muted">Installed at: {selectedApp.installed_at}</div>
                    ) : undefined}
                  </>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      ) : undefined}
    </Container>
  );
}
