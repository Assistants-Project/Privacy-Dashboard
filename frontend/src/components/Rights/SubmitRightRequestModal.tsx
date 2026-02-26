import { useEffect, useState } from "react";
import { Alert, Button, Card, Form, Modal, Spinner } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { buildPredefinedRightMessage, RIGHT_TYPE_LABELS, RightType } from "../../models/request";
import { submitRightRequest } from "../../services/RightsService";
import { useAuth } from "../../contexts/AuthContext";
import { useApp } from "../../contexts/AppsContext";
import { useHome } from "../../contexts/HomeContext";

type SubmitRightRequestModalProps = {
  show: boolean;
  onHide: () => void;
  initialRightType?: RightType;
  initialSelectedConsents?: string[];
  lockRightType?: boolean;
  redirectToRightsOnSubmit?: boolean;
};

function SubmitRightRequestModal({
  show,
  onHide,
  initialRightType,
  initialSelectedConsents,
  lockRightType = false,
  redirectToRightsOnSubmit = true,
}: SubmitRightRequestModalProps) {

  const navigate = useNavigate();
  
  const { user, isDataSubject } = useAuth();
  const { selectedApp, ConsentStatesByAppUUID, loadApps, loadConsentsByApplication } = useApp();
  const { current_home_uuid } = useHome();

  const [rightType, setRightType] = useState<RightType>(RightType.ACCESS_DATA);
  const [message, setMessage] = useState<string>("");
  const [selectedConsents, setSelectedConsents] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | undefined>(undefined);

  const consentStatesForSelectedApp = selectedApp?.uuid ? ConsentStatesByAppUUID[selectedApp.uuid] : undefined;

  const givenConsents = (consentStatesForSelectedApp ?? []).filter((consentState) => consentState.given === true);

  useEffect(() => {
    if (!show) return;
    const nextRightType = initialRightType ?? RightType.ACCESS_DATA;
    setRightType(nextRightType);
    setMessage(buildPredefinedRightMessage(nextRightType, selectedApp?.name));
    setSelectedConsents(
      nextRightType === RightType.WITHDRAW_CONSENT ? (initialSelectedConsents ?? []) : [],
    );
    setSubmitting(false);
    setError(undefined);
  }, [show, selectedApp?.name, initialRightType, initialSelectedConsents]);

  const toggleSelectedConsent = (consentUuid: string) => {
    setSelectedConsents((prev) =>
      prev.includes(consentUuid)
        ? prev.filter((selectedConsentUuid) => selectedConsentUuid !== consentUuid)
        : [...prev, consentUuid],
    );
  };

  const selectAllConsents = () => {
    setSelectedConsents(givenConsents.map((givenConsent) => givenConsent.uuid));
  };

  const clearSelectedConsents = () => {
    setSelectedConsents([]);
  };

  const handleSubmit = async () => {
    if (!user || !isDataSubject) return;
    if (!current_home_uuid) {
      setError("No home selected.");
      return;
    }
    if (!selectedApp?.uuid) {
      setError("No application selected.");
      return;
    }
    
    if (rightType === RightType.WITHDRAW_CONSENT && selectedConsents.length === 0) {
      setError("Please select at least one consent to withdraw.");
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
        ...(rightType === RightType.WITHDRAW_CONSENT
          ? { selected_consents: selectedConsents }
          : {}),
      });

      await loadApps(selectedApp.uuid, true);
      await loadConsentsByApplication(selectedApp.uuid, true);
      onHide();
      if (redirectToRightsOnSubmit) navigate("/rights");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected Error");
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
            disabled={lockRightType}
            onChange={(e) => {
              const next = e.target.value as RightType;
              setRightType(next);
              setMessage(buildPredefinedRightMessage(next, selectedApp?.name));
              if (next !== RightType.WITHDRAW_CONSENT) setSelectedConsents([]);
            }}
          >
            {Object.values(RightType).map((rt) => (
              <option key={rt} value={rt}>
                {RIGHT_TYPE_LABELS[rt]}
              </option>
            ))}
          </Form.Select>
        </Form.Group>

        {rightType === RightType.WITHDRAW_CONSENT ? (
          <Card className="p-0">
            <Card.Body className="d-flex flex-column gap-2">
              <div className="small text-muted">
                By sending the request, the selected consent(s) will be automatically revoked.
              </div>
              <div className="d-flex justify-content-between align-items-center">
                <strong>Select consent(s) to withdraw</strong>
                <div className="d-inline-flex gap-2">
                  <Button
                    size="sm"
                    variant="outline-secondary"
                    onClick={selectAllConsents}
                    disabled={givenConsents.length === 0}
                  >
                    Select all
                  </Button>
                  <Button
                    size="sm"
                    variant="outline-secondary"
                    onClick={clearSelectedConsents}
                    disabled={selectedConsents.length === 0}
                  >
                    Clear
                  </Button>
                </div>
              </div>

              {givenConsents.length > 0 ? (
                <div className="d-flex flex-column gap-2">
                  {givenConsents.map((givenConsent) => (
                    <Form.Check
                      key={givenConsent.uuid}
                      type="checkbox"
                      id={`selected-consent-${givenConsent.uuid}`}
                      checked={selectedConsents.includes(givenConsent.uuid)}
                      onChange={() => toggleSelectedConsent(givenConsent.uuid)}
                      label={givenConsent.content}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-muted">
                  No given consents available for this app in the selected Smart Home.
                </div>
              )}
            </Card.Body>
          </Card>
        ) : undefined}

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
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={
            submitting ||
            (rightType === RightType.WITHDRAW_CONSENT &&
              selectedConsents.length === 0)
          }
        >
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
