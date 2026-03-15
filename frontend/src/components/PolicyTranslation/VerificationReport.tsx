import React from "react";
import { Modal, Button, Alert, ListGroup, Badge } from "react-bootstrap";

interface VerificationReportProps {
  show: boolean;
  onHide: () => void;
  report: any; // The JSON response from /check endpoint
  onDeleteRule: (id: number) => void;
}

const VerificationReport: React.FC<VerificationReportProps> = ({
  show,
  onHide,
  report,
  onDeleteRule,
}) => {
  if (!report) return null;

  const hasProblems =
    (report.loops && report.loops.length > 0) ||
    (report.inconsistentRules && report.inconsistentRules.length > 0) ||
    (report.redundantRules && report.redundantRules.length > 0);

  // Helper to render details list
  const renderDetails = (details: any[]) => {
    if (!details || details.length === 0) return null;
    return (
      <div className="ps-4 mt-1 text-muted small">
        {details.map((d: any, idx: number) => {
          let val = d.value;
          if (typeof val === "object" && val !== null) {
            val = val.name || val.id || JSON.stringify(val);
          }
          return (
            <div key={idx}>
              • <span className="fw-semibold">{d.name}:</span> {val}
            </div>
          );
        })}
      </div>
    );
  };

  // Helper to render rule string
  const renderRuleString = (rule: any, ruleIndex?: number) => {
    const effect = rule.effect === "permit" ? "PERMIT" : "DENY";
    const badgeClass = rule.effect === "permit" ? "success" : "danger";
    const triggerName =
      rule.trigger?.name || rule.trigger?.service?.name || "Unknown Trigger";
    const actionName =
      rule.action?.name || rule.action?.service?.name || "Unknown Action";

    return (
      <div className="w-100">
        <div className="d-flex align-items-center">
          <span className="text-muted small fw-bold  me-2">
            ID {rule.db_id}
          </span>
          <Badge bg={badgeClass} className="me-2" style={{ minWidth: "60px" }}>
            {effect}
          </Badge>
          {!!rule.consent_uuid && (
            <Badge
              bg="secondary"
              className="me-2"
              title={`Consent rule (managed automatically)\nConsent UUID: ${rule.consent_uuid}`}
            >
              CONSENT RULE
            </Badge>
          )}
          <span>
            If <strong>{triggerName}</strong> then <strong>{actionName}</strong>
          </span>
        </div>

        {/* Render Parameters */}
        {rule.trigger?.details && renderDetails(rule.trigger.details)}
        {rule.action?.details && renderDetails(rule.action.details)}
      </div>
    );
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          Policy Verification Report
          {!hasProblems && (
            <Badge bg="success" className="ms-2">
              PASSED
            </Badge>
          )}
          {hasProblems && (
            <Badge bg="danger" className="ms-2">
              ISSUES FOUND
            </Badge>
          )}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {!hasProblems && (
          <Alert variant="success">
            <i className="fa fa-check-circle me-2"></i>
            No issues detected!
          </Alert>
        )}

        {/* LOOPS */}
        {report.loops && report.loops.length > 0 && (
          <div className="mb-4">
            <h5 className="text-danger">
              <i className="fa fa-refresh me-2"></i>Infinite Loops Detected
            </h5>
            <Alert variant="danger">
              The following sequences of rules create infinite loops, which can
              destabilize the system.
            </Alert>
            {report.loops.map((loop: any[], idx: number) => (
              <ListGroup key={idx} className="mb-2">
                <ListGroup.Item variant="danger">
                  <strong>Loop #{idx + 1}</strong>
                </ListGroup.Item>
                {loop.map((rule, rIdx) => (
                  <ListGroup.Item key={rIdx}>
                    {renderRuleString(rule, rIdx)}
                  </ListGroup.Item>
                ))}
              </ListGroup>
            ))}
          </div>
        )}

        {/* INCONSISTENCIES */}
        {report.inconsistentRules && report.inconsistentRules.length > 0 && (
          <div className="mb-4">
            <h5 className="text-warning">
              <i className="fa fa-exclamation-triangle me-2"></i>Inconsistent
              Rules
            </h5>
            <Alert variant="warning">These rules have conflicting logic.</Alert>
            {report.inconsistentRules.map((group: any[], gIdx: number) => (
              <ListGroup key={gIdx} className="mb-3">
                <ListGroup.Item variant="warning">
                  <strong>Conflict Group #{gIdx + 1}</strong>
                </ListGroup.Item>
                {group.map((rule: any, rIdx: number) => (
                  <ListGroup.Item
                    key={rIdx}
                    className="d-flex justify-content-between align-items-center"
                  >
                    <div className="flex-grow-1">
                      {renderRuleString(rule, rIdx)}
                    </div>
                    <Button
                      variant="danger"
                      size="sm"
                      className="ms-3 text-nowrap"
                      disabled={!!rule.consent_uuid}
                      title={
                        rule.consent_uuid
                          ? "This rule is linked to a consent and cannot be deleted"
                          : "Delete"
                      }
                      onClick={() => {
                        if (rule.consent_uuid) return;
                        onDeleteRule(rule.db_id);
                      }}
                    >
                      <i className="fa fa-trash me-1"></i> Delete
                    </Button>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            ))}
          </div>
        )}

        {/* REDUNDANCIES */}
        {report.redundantRules && report.redundantRules.length > 0 && (
          <div className="mb-4">
            <h5 className="text-info">
              <i className="fa fa-clone me-2"></i>Redundant Rules
            </h5>
            <Alert variant="info">
              These rules perform the exact same logic.
            </Alert>
            {report.redundantRules.map((group: any[], gIdx: number) => (
              <ListGroup key={gIdx} className="mb-3">
                <ListGroup.Item variant="info">
                  <strong>Redundancy Group #{gIdx + 1}</strong>
                </ListGroup.Item>
                {group.map((rule: any, rIdx: number) => (
                  <ListGroup.Item
                    key={rIdx}
                    className="d-flex justify-content-between align-items-center"
                  >
                    <div className="flex-grow-1">
                      {renderRuleString(rule, rIdx)}
                    </div>
                    <Button
                      variant="danger"
                      size="sm"
                      className="ms-3 text-nowrap"
                      disabled={!!rule.consent_uuid}
                      title={
                        rule.consent_uuid
                          ? "This rule is linked to a consent and cannot be deleted"
                          : "Delete"
                      }
                      onClick={() => {
                        if (rule.consent_uuid) return;
                        onDeleteRule(rule.db_id);
                      }}
                    >
                      <i className="fa fa-trash me-1"></i> Delete
                    </Button>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            ))}
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default VerificationReport;
