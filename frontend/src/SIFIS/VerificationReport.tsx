import React from "react";
import { Modal, Button, Alert, ListGroup, Badge } from "react-bootstrap";

interface VerificationReportProps {
  show: boolean;
  onHide: () => void;
  report: any; // The JSON response from /check endpoint
}

const VerificationReport: React.FC<VerificationReportProps> = ({ show, onHide, report }) => {
  if (!report) return null;

  const hasProblems = 
    (report.loops && report.loops.length > 0) || 
    (report.inconsistentRules && report.inconsistentRules.length > 0) || 
    (report.redundantRules && report.redundantRules.length > 0);

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
            Policy Verification Report
            {!hasProblems && <Badge bg="success" className="ms-2">PASSED</Badge>}
            {hasProblems && <Badge bg="danger" className="ms-2">ISSUES FOUND</Badge>}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {!hasProblems && (
            <Alert variant="success">
                <i className="fa fa-check-circle me-2"></i>
                No issues found. The policy logic is sound.
            </Alert>
        )}

        {/* LOOPS */}
        {report.loops && report.loops.length > 0 && (
          <div className="mb-4">
            <h5 className="text-danger"><i className="fa fa-refresh me-2"></i>Infinite Loops Detected</h5>
            <Alert variant="danger">
               The following sequences of rules create infinite loops, which can destabilize the system.
            </Alert>
            {report.loops.map((loop: any[], idx: number) => (
                <ListGroup key={idx} className="mb-2">
                    <ListGroup.Item variant="danger"><strong>Loop #{idx + 1}</strong></ListGroup.Item>
                    {loop.map((rule, rIdx) => (
                        <ListGroup.Item key={rIdx}>
                            {rIdx + 1}. If <strong>{rule.trigger?.service_name}</strong> then <strong>{rule.action?.service_name}</strong>
                        </ListGroup.Item>
                    ))}
                </ListGroup>
            ))}
          </div>
        )}

        {/* INCONSISTENCIES */}
        {report.inconsistentRules && report.inconsistentRules.length > 0 && (
          <div className="mb-4">
             <h5 className="text-warning"><i className="fa fa-exclamation-triangle me-2"></i>Inconsistent Rules</h5>
             <Alert variant="warning">
                These rules have conflicting logic (e.g., trying to do different things with the same trigger).
             </Alert>
             <ListGroup>
                {report.inconsistentRules.map((rule: any, idx: number) => (
                    <ListGroup.Item key={idx}>
                         If <strong>{rule.trigger?.service_name}</strong> then <strong>{rule.action?.service_name}</strong> (ID: {rule.db_id})
                    </ListGroup.Item>
                ))}
             </ListGroup>
          </div>
        )}

        {/* REDUNDANCIES */}
        {report.redundantRules && report.redundantRules.length > 0 && (
          <div className="mb-4">
             <h5 className="text-info"><i className="fa fa-clone me-2"></i>Redundant Rules</h5>
             <Alert variant="info">
                These rules perform the exact same logic. Consider removing duplicates.
             </Alert>
             <ListGroup>
                {report.redundantRules.map((rule: any, idx: number) => (
                    <ListGroup.Item key={idx}>
                         If <strong>{rule.trigger?.service_name}</strong> then <strong>{rule.action?.service_name}</strong> (ID: {rule.db_id})
                    </ListGroup.Item>
                ))}
             </ListGroup>
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
