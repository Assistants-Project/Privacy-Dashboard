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
  const [searchParams] = useSearchParams();
  const statusFromURL = (searchParams.get("status") ?? "").trim().toUpperCase();
  const statusFilterFromURL: RequestStatus | undefined =
    statusFromURL === RequestStatus.PENDING || statusFromURL === RequestStatus.HANDLED
      ? (statusFromURL as RequestStatus)
      : undefined;
  const [statusFilter, setStatusFilter] = useState<RequestStatus | undefined>(statusFilterFromURL);
  const {requests,loadingRequests,errorRequests,loadRequests} = useRightsRequests(statusFilter); //carica l'hook

  const [selectedRequestUuid, setSelectedRequestUuid] = useState<string | undefined>(undefined);
  const selectedItem = selectedRequestUuid? requests?.find((r) => r.request.uuid === selectedRequestUuid): undefined;
  const selectedRequest = selectedItem?.request;

  const closePanel = () => setSelectedRequestUuid(undefined);

  const statusBadge = (status: RequestStatus) => {
    if (status === RequestStatus.HANDLED) return "success";
    return "warning";
  };

  useEffect(() => {
    setStatusFilter(statusFilterFromURL);
  }, [statusFilterFromURL]);


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
          <RightsRequestsListPanel
            requests={requests}
            selectedRequestUuid={selectedRequestUuid}
            onSelectRequest={setSelectedRequestUuid}
            statusFilter={statusFilter}
            onStatusFilterChange={setStatusFilter}
          />

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

                    {isManagerRole ? (
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
