import {Badge,Card,CloseButton,Col,Container,Form,Row,Spinner} from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { Role } from "../../models/user";
import { useState } from "react";
import { RequestStatus, RIGHT_TYPE_LABELS } from "../../models/request";
import { RightRequestHandleForm } from "../../components/Rights/RightRequestHandleForm";
import { useRightsRequests } from "../../hooks/useRightsRequests";
import { formatIsoDateOrTime } from "../../services/MessageService";

export function ManageRights() {

  const { user, loading } = useAuth();
  const [statusFilter, setStatusFilter] = useState<RequestStatus | undefined>(undefined);
  const {requests,loadingRequests,errorRequests,loadRequests} = useRightsRequests(statusFilter); //carica l'hook

  const [selectedRequestUuid, setSelectedRequestUuid] = useState<string | undefined>(undefined);
  const selectedItem = selectedRequestUuid? requests?.find((r) => r.request.uuid === selectedRequestUuid): undefined;
  const selectedRequest = selectedItem?.request;
  
  const [query, setQuery] = useState<string>("");
  //filtro semplice: cerchiamo solo per nome applicazione
  const visibleRequests = requests?.filter((item) => item.application_name?.toLowerCase().includes(query));

  const closePanel = () => setSelectedRequestUuid(undefined);
  const isDataSubject = user?.role === Role.DataSubject;
  const isManager = user?.role === Role.DataController || user?.role === Role.DPO;

  const statusBadge = (status: RequestStatus) => {
    if (status === RequestStatus.HANDLED) return "success";
    return "warning";
  };


  return (
    <Container fluid className="py-3">
      {loadingRequests ? (
        <Card className="mb-3 p-0">
          <Card.Body className="d-inline-flex align-items-center gap-2">
            <Spinner animation="border" size="sm" />
            Loading…
          </Card.Body>
        </Card>
      ) : undefined}

      {errorRequests ? (
        <Card bg="danger" text="white" className="mb-3 p-0">
          <Card.Body>{errorRequests}</Card.Body>
        </Card>
      ) : undefined}

      {!loading && !loadingRequests && !errorRequests ? (
        <Row className="g-3 align-items-start">
          <Col xs={12} lg={5}>
            <Container fluid className="d-flex flex-column gap-3">
              <Card className="p-0">
                <Card.Body className="d-flex flex-column gap-3">
                  <Form.Group controlId="requests-search">
                    <Form.Label className="mb-1">Search</Form.Label>
                    <Form.Control
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="App name…"
                    />
                  </Form.Group>

                  <Form.Group controlId="requests-status">
                    <Form.Label className="mb-1">Status</Form.Label>
                    <Form.Select
                      value={statusFilter ?? ""}
                      onChange={(e) =>
                        setStatusFilter(
                          e.target.value
                            ? (e.target.value as RequestStatus)
                            : undefined,
                        )
                      }
                    >
                      <option value="">All</option>
                      <option value={RequestStatus.PENDING}>Pending</option>
                      <option value={RequestStatus.HANDLED}>Handled</option>
                    </Form.Select>
                  </Form.Group>
                </Card.Body>
              </Card>

              {visibleRequests?.length === 0 ? (
                <Card className="p-0">
                  <Card.Body className="text-muted">
                    No requests.
                  </Card.Body>
                </Card>
              ) : (
                <Container fluid className="d-flex flex-column gap-2 p-0">
                  {visibleRequests?.map((item) => {
                    const selected = item.request.uuid === selectedRequestUuid;
                    const rightLabel = RIGHT_TYPE_LABELS[item.request.right_type] ?? item.request.right_type;
                    return (
                      <Card
                        key={item.request.uuid}
                        role="button"
                        tabIndex={0}
                        onClick={() => {
                          if (selected) {
                            closePanel();
                            return;
                          }
                          setSelectedRequestUuid(item.request.uuid);
                        }}
                        className={[
                          "p-0 apps_card_hover",
                          selected ? "border-3 apps_card_selected" : "",
                        ].join(" ")}
                        style={{ cursor: "pointer" }}
                      >
                        <Card.Body className="d-flex flex-column gap-1">
                          <div className="d-flex justify-content-between gap-3">
                            <div className="flex-grow-1">
                              <strong>{item.application_name}</strong>
                              <div className="text-muted">{rightLabel}</div>
                            </div>
                            <div className="text-end">
                              <Badge bg={statusBadge(item.request.status)}>
                                {item.request.status}
                              </Badge>
                              <div className="text-muted small">
                                {formatIsoDateOrTime(item.request.created_at, true)}
                              </div>
                            </div>
                          </div>

                          {isManager ? (
                            <div className="text-muted small">
                              {item.user_email}
                            </div>
                          ) : undefined}
                        </Card.Body>
                      </Card>
                    );
                  })}
                </Container>
              )}
            </Container>
          </Col>

          <Col xs={12} lg={7}>
            <Card className="sticky-top z-1 p-0" style={{ top: "1rem" }}>
              <Card.Body className="d-flex flex-column gap-3">
                {!selectedItem ? (
                  <div className="text-muted">
                    Select a request to see details.
                  </div>
                ) : (
                  <>
                    <Container
                      fluid
                      className="d-flex px-0 justify-content-between align-items-start"
                    >
                      <Container fluid className="ps-0">
                        <h2 className="h4 mb-1">{selectedItem.application_name}</h2>
                        <div className="d-flex align-items-center gap-2">
                          <Badge bg={statusBadge(selectedRequest!.status)}>
                            {selectedRequest!.status}
                          </Badge>
                          <span className="text-muted">
                            {RIGHT_TYPE_LABELS[selectedRequest!.right_type]}
                          </span>
                        </div>
                      </Container>
                      <CloseButton onClick={closePanel} />
                    </Container>

                    {isManager ? (
                      <div className="text-muted">
                        Requester: <strong>{selectedItem.user_email}</strong>
                      </div>
                    ) : undefined}

                    <div className="text-muted">
                      Created at:{" "}
                      <strong>
                        {formatIsoDateOrTime(selectedRequest!.created_at, true)}
                      </strong>
                    </div>

                    {selectedRequest!.handled_at ? (
                      <div className="text-muted">
                        Handled at:{" "}
                        <strong>
                          {formatIsoDateOrTime(selectedRequest!.handled_at, true)}
                        </strong>
                      </div>
                    ) : undefined}

                    <Card className="p-0">
                      <Card.Body>
                        <strong>Request message</strong>
                        <div
                          className="mt-2 text-muted"
                          style={{ whiteSpace: "pre-wrap" }}
                        >
                          {selectedRequest!.additional_information}
                        </div>
                      </Card.Body>
                    </Card>

                    {selectedRequest!.response ? (
                      <Card className="p-0">
                        <Card.Body>
                          <strong>Response</strong>
                          <div
                            className="mt-2 text-muted"
                            style={{ whiteSpace: "pre-wrap" }}
                          >
                            {selectedRequest!.response}
                          </div>
                        </Card.Body>
                      </Card>
                    ) : (
                      <Card className="p-0">
                        <Card.Body className="text-muted">
                          No response yet.
                        </Card.Body>
                      </Card>
                    )}

                    {isManager ? (
                      selectedRequest ? (
                        <RightRequestHandleForm request={selectedRequest} onSaved={loadRequests} />
                      ) : undefined
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
