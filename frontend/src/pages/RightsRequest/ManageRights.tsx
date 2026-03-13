import {Badge,Card,CloseButton,Col,Container,Row,Spinner} from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { RequestStatus, RIGHT_TYPE_LABELS, RightType } from "../../models/request";
import { RightRequestHandleForm } from "../../components/Rights/RightRequestHandleForm";
import { RightsRequestsListPanel } from "../../components/Rights/RightsRequestsListPanel";
import { useRightsRequests } from "../../hooks/useRightsRequests";
import { formatIsoDateOrTime } from "../../services/MessageService";

export function ManageRights() {

  const { loading, isManagerRole } = useAuth();
  const getRequesterName = (firstname?: string, lastname?: string, fallback?: string) =>
    [firstname, lastname].filter((value): value is string => !!value && value.trim() !== "").join(" ").trim() || fallback || "Unknown requester";
  const [searchParams] = useSearchParams();
  const statusFromURL = (searchParams.get("status") ?? "").trim().toUpperCase();
  const requestUuidFromURL = (searchParams.get("request") ?? "").trim() || undefined;
  const statusFilterFromURL: RequestStatus | undefined =
    statusFromURL === RequestStatus.PENDING || statusFromURL === RequestStatus.HANDLED
      ? (statusFromURL as RequestStatus)
      : undefined;
  const [statusFilter, setStatusFilter] = useState<RequestStatus | undefined>(statusFilterFromURL);
  const {requests,loadingRequests,errorRequests,loadRequests} = useRightsRequests(statusFilter); //carica l'hook

  const [selectedRequestUuid, setSelectedRequestUuid] = useState<string | undefined>(requestUuidFromURL);
  const selectedItem = selectedRequestUuid? requests?.find((r) => r.request.uuid === selectedRequestUuid): undefined;
  const selectedRequest = selectedItem?.request;
  const requesterName = selectedItem ? getRequesterName(selectedItem.user_firstname, selectedItem.user_lastname, selectedItem.user_email) : undefined;

  const closePanel = () => setSelectedRequestUuid(undefined);

  const statusBadge = (status: RequestStatus) => {
    if (status === RequestStatus.HANDLED) return "success";
    return "warning";
  };

  useEffect(() => {
    setStatusFilter(statusFilterFromURL);
  }, [statusFilterFromURL]);

  useEffect(() => {
    setSelectedRequestUuid(requestUuidFromURL);
  }, [requestUuidFromURL]);


  return (
    <Container fluid className="py-2 d-flex flex-column overflow-hidden h-100" style={{ minHeight: 0 }}>
      {loadingRequests ? (
        <Card className="mb-3 p-0 flex-shrink-0">
          <Card.Body className="d-inline-flex align-items-center gap-2">
            <Spinner animation="border" size="sm" />
            Loading…
          </Card.Body>
        </Card>
      ) : undefined}

      {errorRequests ? (
        <Card bg="danger" text="white" className="mb-3 p-0 flex-shrink-0">
          <Card.Body>{errorRequests}</Card.Body>
        </Card>
      ) : undefined}

      {!loading && !loadingRequests && !errorRequests ? (
        <Row className="g-3 align-items-start align-items-lg-stretch flex-grow-1 overflow-hidden" style={{ minHeight: 0 }}>
          <RightsRequestsListPanel
            requests={requests}
            selectedRequestUuid={selectedRequestUuid}
            onSelectRequest={setSelectedRequestUuid}
            statusFilter={statusFilter}
            onStatusFilterChange={setStatusFilter}
          />

          <Col xs={12} lg={7} className="d-flex flex-column overflow-hidden ps-lg-1" style={{ minHeight: 0 }}>
            <Card
              className={selectedItem ? "p-0 d-flex flex-column h-100 overflow-hidden" : "p-0"}
              style={selectedItem ? { minHeight: 0 } : undefined}
            >
              <Card.Body
                className={selectedItem ? "d-flex flex-column gap-3 flex-grow-1 overflow-auto" : "d-flex flex-column gap-3"}
                style={selectedItem ? { minHeight: 0 } : undefined}
              >
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

                    {isManagerRole ? (
                      <div className="text-muted">
                        Requester: <strong>{requesterName}</strong>
                      </div>
                    ) : undefined}

                    {isManagerRole ? (
                      <div className="text-muted">
                        Requester email: <strong>{selectedItem.user_email}</strong>
                      </div>
                    ) : undefined}

                    {isManagerRole ? (
                      <div className="text-muted" title={selectedItem.processing_context_uuid}>
                        Context ID:{" "}
                        <strong className="font-monospace">
                          {selectedItem.processing_context_uuid}
                        </strong>
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

                    {selectedRequest!.right_type === RightType.WITHDRAW_CONSENT ? (
                        <Card className="p-0">
                        <Card.Body>
                          <strong>Selected consents to withdraw</strong>
                          {selectedRequest!.selected_consents?.length ? (
                            <ul className="mt-2 mb-0">
                              {selectedRequest!.selected_consents.map((consent) => (
                                <li key={consent.uuid}>
                                  {consent.content?.trim() ? consent.content : consent.uuid}
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <div className="mt-2 text-muted">No consents selected.</div>
                          )}
                        </Card.Body>
                      </Card>
                    ) : undefined}

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

                    {isManagerRole ? (
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
