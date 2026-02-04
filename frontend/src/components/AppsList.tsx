import { useEffect, useState } from "react";
import { Button, Card, Col, Container, Form, Row, Spinner, Stack } from "react-bootstrap";
import { RequestModel, RequestStatus } from "../models/request";
import { handleRightRequest } from "../services/RightsService";
import { useApp } from "./AppsContext";


function AppsList(props: any) {

    const { loadPrivacyNotice, PrivacyNoticeByAppUUID, managedApps, selectedAppUUID, setSelectedAppUUID, loadingApps, selectedApp } = useApp();
    const [query, setQuery] = useState("");

  return (
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

                  {(managedApps.length ?? 0) === 0 ? (
                    <Card className="p-0">
                      <Card.Body className="text-muted">No managed apps.</Card.Body>
                    </Card>
                  ) : (
                    <Stack
                      className="overflow-auto pe-3"
                      style={{ maxHeight: "calc(100vh - 12rem)" }}
                    >
                      <Row xs={1} md={1} className="g-4">
                        {managedApps
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
                            const description = app.description;

                            return (
                              <Col key={app.uuid}>
                                <Card
                                  role="button"
                                  tabIndex={0}
                                  onClick={() => {
                                    if (selected) {
                                      props.closePanel();
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
                    </Stack>
                  )}
                </Container>
  );
}

export { AppsList };

