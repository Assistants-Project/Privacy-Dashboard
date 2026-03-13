import { Badge, Card, Col, Container, Form } from "react-bootstrap";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { RequestStatus, RIGHT_TYPE_LABELS } from "../../models/request";
import { formatIsoDateOrTime } from "../../services/MessageService";
import { RequestListItem } from "../../services/RightsService";

type RightsRequestsListPanelProps = {
  requests: RequestListItem[] | undefined;
  selectedRequestUuid: string | undefined;
  onSelectRequest: (requestUuid: string | undefined) => void;
  statusFilter: RequestStatus | undefined;
  onStatusFilterChange: (status: RequestStatus | undefined) => void;
};

export function RightsRequestsListPanel({ requests, selectedRequestUuid, onSelectRequest, statusFilter, onStatusFilterChange }: RightsRequestsListPanelProps) {
  const { isManagerRole } = useAuth();
  const [searchParams] = useSearchParams();
  const appFilterFromURL = (searchParams.get("app") ?? "").trim();
  const [query, setQuery] = useState<string>(appFilterFromURL);
  const normalizedQuery = useMemo(() => query.trim().toLowerCase(), [query]);
  const visibleRequests = requests?.filter((item) => {
    if (!normalizedQuery) return true;

    return [
      item.application_name,
      item.user_email,
      item.processing_context_uuid,
      RIGHT_TYPE_LABELS[item.request.right_type] ?? item.request.right_type,
    ]
      .filter((value): value is string => typeof value === "string")
      .some((value) => value.toLowerCase().includes(normalizedQuery));
  });

  const statusBadge = (status: RequestStatus) => {
    if (status === RequestStatus.HANDLED) return "success";
    return "warning";
  };

  useEffect(() => {
    setQuery(appFilterFromURL);
  }, [appFilterFromURL]);

  return (
    <Col xs={12} lg={5} className="d-flex flex-column overflow-hidden" style={{ minHeight: 0 }}>
      <Container fluid className="d-flex flex-column gap-3 p-0 flex-grow-1 overflow-hidden" style={{ minHeight: 0 }}>
        <Card className="p-0 flex-shrink-0">
          <Card.Body className="d-flex flex-column gap-3">
            <Form.Group controlId="requests-search">
              <Form.Label className="mb-1">Search</Form.Label>
              <Form.Control
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="App, requester, context ID…"
              />
            </Form.Group>

            <Form.Group controlId="requests-status">
              <Form.Label className="mb-1">Status</Form.Label>
              <Form.Select value={statusFilter ?? ""} onChange={(e) => onStatusFilterChange(e.target.value ? (e.target.value as RequestStatus) : undefined)}>
                <option value="">All</option>
                <option value={RequestStatus.PENDING}>Pending</option>
                <option value={RequestStatus.HANDLED}>Handled</option>
              </Form.Select>
            </Form.Group>
          </Card.Body>
        </Card>

        {visibleRequests?.length === 0 ? (
          <Card className="p-0 flex-shrink-0">
            <Card.Body className="text-muted">
              No requests.
            </Card.Body>
          </Card>
        ) : (
          <Container
            fluid
            className="d-flex flex-column gap-2 ps-0 pe-3 pb-0 pt-0 flex-grow-1 overflow-auto"
            style={{ minHeight: 0, height: 0 }}
          >
            {visibleRequests?.map((item) => {
              const selected = item.request.uuid === selectedRequestUuid;
              const rightLabel = RIGHT_TYPE_LABELS[item.request.right_type] ?? item.request.right_type;
              const shortContextId = item.processing_context_uuid.slice(0, 8);
              return (
                <Card
                  key={item.request.uuid}
                  role="button"
                  tabIndex={0}
                  onClick={() => onSelectRequest(selected ? undefined : item.request.uuid)}
                  className={["p-0 apps_card_hover", selected ? "border-3 apps_card_selected" : ""].join(" ")}
                  style={{ cursor: "pointer" }}
                >
                  <Card.Body className="d-flex flex-column gap-1">
                    <div className="d-flex justify-content-between align-items-center gap-3">
                      <div className="flex-grow-1">
                        <div className="d-flex flex-wrap align-items-center gap-2">
                          <strong>{item.application_name}</strong>
                          <span className="text-muted">{rightLabel}</span>
                        </div>
                      </div>
                      <div className="d-flex align-items-center gap-2 flex-shrink-0">
                        <Badge bg={statusBadge(item.request.status)}>
                          {item.request.status}
                        </Badge>
                        <div className="text-muted small">
                          {formatIsoDateOrTime(item.request.created_at, true)}
                        </div>
                      </div>
                    </div>

                    {isManagerRole ? (
                      <>
                        <div className="text-muted small">
                          Requester: <span className="fw-medium text-body">{item.user_email}</span>
                        </div>
                        <div className="text-muted small" title={item.processing_context_uuid}>
                          Context ID: <span className="font-monospace">{shortContextId}</span>
                        </div>
                      </>
                    ) : undefined}
                  </Card.Body>
                </Card>
              );
            })}
          </Container>
        )}
      </Container>
    </Col>
  );
}
