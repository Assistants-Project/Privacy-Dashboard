import { useEffect, useMemo, useState } from "react";
import { Card, Col, Pagination, Row } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { useApp } from "../../contexts/AppsContext";
import { DocumentStatus } from "../../models/app";

export function AppsOverviewPanel() {
  const { isDataSubject } = useAuth();
  const navigate = useNavigate();
  const { apps, setSelectedAppUUID } = useApp();

  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = isDataSubject ? 6 : 8;

  const allApps = apps ?? [];

  const appsNeedingAttention = useMemo(() => {
    if (isDataSubject) {
      return allApps.filter((app) => (app.pending_right_requests_count ?? 0) > 0);
    }

    return allApps.filter(
      (app) =>
        app.pn_status === DocumentStatus.Missing ||
        app.pia_status === DocumentStatus.Missing ||
        !app.evaluation ||
        (app.pending_right_requests_count ?? 0) > 0,
    );
  }, [allApps, isDataSubject]);

  const totalPages = useMemo(
    () => Math.max(1, Math.ceil(appsNeedingAttention.length / pageSize)),
    [appsNeedingAttention.length],
  );

  useEffect(() => {
    setCurrentPage(1);
  }, [appsNeedingAttention.length]);

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  const pagedAppsNeedingAttention = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return appsNeedingAttention.slice(start, start + pageSize);
  }, [appsNeedingAttention, currentPage]);

  return (
    <div className="h-100 d-flex flex-column mb-3">
      <Row className="pt-2 mb-2">
        <Col className="d-flex align-items-baseline gap-2">
          <h2 className="mb-0">{isDataSubject ? "Pending Right Requests" : "Apps Overview"}</h2>
          {isDataSubject ? (
            <span className="text-muted">| Your installed apps with pending right requests</span>
          ) : undefined}
        </Col>
      </Row>

      {!isDataSubject ? (
        <Row className="mb-3">
          <Col>
            <div className="text-muted">
              Legend: <span className="text-success"> green</span> = document available / no pending requests | <span className="text-danger">red</span> = document missing.
            </div>
          </Col>
        </Row>
      ) : undefined}

      {appsNeedingAttention.length === 0 ? (
        <Row>
          <Col>
            <div className="text-muted mt-3">No Apps Needs Attention</div>
          </Col>
        </Row>
      ) : (
        <>
          <div className="flex-grow-1 mt-2" style={{ minHeight: 0 }}>
            <Row xs={1} md={2} className="g-3">
              {pagedAppsNeedingAttention.map((app) => {
                const pendingRequestsCount = app.pending_right_requests_count ?? 0;
                const hasPendingRequests = pendingRequestsCount > 0;

                const pnAvailable = app.pn_status === DocumentStatus.Available;
                const piaAvailable = app.pia_status === DocumentStatus.Available;
                const questionnaireAvailable = !!app.evaluation;

                const pendingRequestsClassName = hasPendingRequests ? "text-danger" : "text-success";

                return (
                  <Col key={app.uuid}>
                    <Card className="h-100 p-0">
                      <Card.Body>
                        <Row className="align-items-start justify-content-between">
                          <Col>
                            <strong>{app.title}</strong>
                            {app.description ? <div className="text-muted">{app.description}</div> : <div className="text-muted">(no description)</div>}
                          </Col>

                          <Col xs="auto" className="d-flex flex-column align-items-end gap-1">
                            {isDataSubject ? null : (
                              <>
                                <button type="button" className={pnAvailable ? "btn p-0 text-end text-success home-doc-link" : "btn p-0 text-end text-danger home-doc-link"} onClick={() => { setSelectedAppUUID(app.uuid); navigate("/privacy-notice"); }}>Privacy Notice</button>
                                <button type="button" className={piaAvailable ? "btn p-0 text-end text-success home-doc-link" : "btn p-0 text-end text-danger home-doc-link"} onClick={() => { setSelectedAppUUID(app.uuid); navigate("/privacy-impact-assessment"); }}>Privacy Impact Assessment</button>
                                <button type="button" className={questionnaireAvailable ? "btn p-0 text-end text-success home-doc-link" : "btn p-0 text-end text-danger home-doc-link"} onClick={() => { setSelectedAppUUID(app.uuid); navigate("/questionnaire"); }}>Questionnaire</button>
                              </>
                            )}

                            <button type="button" className={`btn p-0 text-end home-doc-link ${pendingRequestsClassName}`} onClick={() => navigate(`/rights?app=${encodeURIComponent(app.name)}${hasPendingRequests ? "&status=PENDING" : ""}`)}>
                              Pending Right Requests{hasPendingRequests ? ` (${pendingRequestsCount})` : ""}
                            </button>
                          </Col>
                        </Row>
                      </Card.Body>
                    </Card>
                  </Col>
                );
              })}
            </Row>
          </div>

          <Row className="justify-content-center mt-3 flex-shrink-0">
            <Col xs="auto">
              <Pagination className="mb-0">
                {Array.from({ length: totalPages }, (_, index) => {
                  const pageNumber = index + 1;
                  return (
                    <Pagination.Item key={pageNumber} active={pageNumber === currentPage} onClick={() => setCurrentPage(pageNumber)}>
                      {pageNumber}
                    </Pagination.Item>
                  );
                })}
              </Pagination>
            </Col>
          </Row>
        </>
      )}
    </div>
  );
}
