import { useEffect, useState } from "react";
import { Alert, Button, Form, Modal, Spinner } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { Role } from "../../models/user";
import { buildPredefinedRightMessage, RIGHT_TYPE_LABELS, RightType } from "../../models/request";
import { submitRightRequest } from "../../services/RightsService";
import { useAuth } from "../Authentication/AuthContext";
import { useApp } from "../AppsContext";
import { useHome } from "../HomeContext";

type SubmitRightRequestModalProps = {
  show: boolean;
  onHide: () => void;
};

function SubmitRightRequestModal({show,onHide}: SubmitRightRequestModalProps) {

  const navigate = useNavigate();
  
  const { user } = useAuth();
  const { selectedApp } = useApp();
  const { current_home_uuid } = useHome();

  const [rightType, setRightType] = useState<RightType>(RightType.ACCESS_DATA);
  const [message, setMessage] = useState<string>("");
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (!show) return;
    setRightType(RightType.ACCESS_DATA);
    setMessage(buildPredefinedRightMessage(RightType.ACCESS_DATA, selectedApp?.name));
    setSubmitting(false);
    setError(undefined);
  }, [show]);

  const handleSubmit = async () => {
    if (!user || user.role !== Role.DataSubject) return;
    if (!current_home_uuid) {
      setError("No home selected.");
      return;
    }
    if (!selectedApp?.uuid) {
      setError("No application selected.");
      return;
    }

    const trimmedMessage = message.trim();
    if (!trimmedMessage) {
      setError("Please write a message.");
      return;
    }

    setSubmitting(true);
    setError(undefined);

    try {
      await submitRightRequest({
        right_type: rightType,
        additional_information: trimmedMessage,
        smart_home_uuid: current_home_uuid,
        application_uuid: selectedApp?.uuid,
      });

      onHide();
      navigate("/rights");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Errore inatteso");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>Exercise a GDPR right</Modal.Title>
      </Modal.Header>

      <Modal.Body className="d-flex flex-column gap-3">
        {error ? <Alert variant="danger" className="mb-0">{error}</Alert> : undefined}

        <div className="text-muted">
          Application: <strong>{selectedApp?.name}</strong>          
        </div>

        <Form.Group controlId="right-type">
          <Form.Label className="mb-1">Right type</Form.Label>
          <Form.Select
            value={rightType}
            onChange={(e) => {
              const next = e.target.value as RightType;
              setRightType(next);
              setMessage(buildPredefinedRightMessage(next, selectedApp?.name));
            }}
          >
            {Object.values(RightType).map((rt) => (
              <option key={rt} value={rt}>
                {RIGHT_TYPE_LABELS[rt]}
              </option>
            ))}
          </Form.Select>
        </Form.Group>

        <Form.Group controlId="message">
          <Form.Label className="mb-1">Message</Form.Label>
          <Form.Control
            as="textarea"
            rows={6}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
        </Form.Group>
      </Modal.Body>

      <Modal.Footer>
        <Button variant="outline-secondary" onClick={onHide} disabled={submitting}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSubmit} disabled={submitting}>
          {submitting ? (
            <span className="d-inline-flex align-items-center gap-2">
              <Spinner animation="border" size="sm" />
              Submitting…
            </span>
          ) : (
            "Submit request"
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export { SubmitRightRequestModal };
