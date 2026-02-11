import { useEffect, useState } from "react";
import { Alert, Button, Card, Form, Modal, Spinner } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { Role } from "../../models/user";
import { buildPredefinedRightMessage, RIGHT_TYPE_LABELS, RightType } from "../../models/request";
import { submitRightRequest } from "../../services/RightsService";
import { useAuth } from "../../contexts/AuthContext";
import { useApp } from "../../contexts/AppsContext";
import { useHome } from "../../contexts/HomeContext";
import { fetchGivenConsentsBySmartHome } from "../../services/AvailableConsentService";
import { GivenConsentInHomeModel } from "../../models/available_consent";

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
  const [givenConsents, setGivenConsents] = useState<GivenConsentInHomeModel[] | undefined>(undefined);
  const [selectedConsents, setSelectedConsents] = useState<string[]>([]);
  const [loadingConsents, setLoadingConsents] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (!show) return;
    setRightType(RightType.ACCESS_DATA);
    setMessage(buildPredefinedRightMessage(RightType.ACCESS_DATA, selectedApp?.name));
    setGivenConsents(undefined);
    setSelectedConsents([]);
    setLoadingConsents(false);
    setSubmitting(false);
    setError(undefined);
  }, [show, selectedApp?.name]);

  useEffect(() => {
    if (!show) return;
    if (rightType !== RightType.WITHDRAW_CONSENT) {
      setGivenConsents(undefined);
      setSelectedConsents([]);
      setLoadingConsents(false);
      return;
    }
    if (!user || user.role !== Role.DataSubject) return;
    if (!current_home_uuid || !selectedApp?.uuid) return;

    let cancelled = false;
    setLoadingConsents(true);
    setError(undefined);

    const loadGivenConsents = async () => {
      try {
        const allGivenConsents = await fetchGivenConsentsBySmartHome(current_home_uuid);
        if (cancelled) return;

        const filteredBySelectedApp = (allGivenConsents ?? []).filter(
          (givenConsent) => givenConsent.application_uuid === selectedApp.uuid,
        );
        setGivenConsents(filteredBySelectedApp);
        setSelectedConsents([]);
      } catch (err) {
        if (cancelled) return;
        setGivenConsents([]);
        setError(err instanceof Error ? err.message : "Errore inatteso");
      } finally {
        if (!cancelled) setLoadingConsents(false);
      }
    };

    void loadGivenConsents();

    return () => {
      cancelled = true;
    };
  }, [show, rightType, selectedApp?.uuid, current_home_uuid, user?.uuid, user?.role]);

  const toggleSelectedConsent = (consentUuid: string) => {
    setSelectedConsents((prev) =>
      prev.includes(consentUuid)
        ? prev.filter((selectedConsentUuid) => selectedConsentUuid !== consentUuid)
        : [...prev, consentUuid],
    );
  };

  const selectAllConsents = () => {
    setSelectedConsents((givenConsents ?? []).map((givenConsent) => givenConsent.available_consent.uuid));
  };

  const clearSelectedConsents = () => {
    setSelectedConsents([]);
  };

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

        {rightType === RightType.WITHDRAW_CONSENT ? (
          <Card className="p-0">
            <Card.Body className="d-flex flex-column gap-2">
              <div className="d-flex justify-content-between align-items-center">
                <strong>Select consent(s) to withdraw</strong>
                <div className="d-inline-flex gap-2">
                  <Button
                    size="sm"
                    variant="outline-secondary"
                    onClick={selectAllConsents}
                    disabled={loadingConsents || !givenConsents?.length}
                  >
                    Select all
                  </Button>
                  <Button
                    size="sm"
                    variant="outline-secondary"
                    onClick={clearSelectedConsents}
                    disabled={loadingConsents || selectedConsents.length === 0}
                  >
                    Clear
                  </Button>
                </div>
              </div>

              {loadingConsents ? (
                <div className="d-inline-flex align-items-center gap-2 text-muted">
                  <Spinner animation="border" size="sm" />
                  Loading given consents…
                </div>
              ) : givenConsents && givenConsents.length > 0 ? (
                <div className="d-flex flex-column gap-2">
                  {givenConsents.map((givenConsent) => (
                    <Form.Check
                      key={givenConsent.available_consent.uuid}
                      type="checkbox"
                      id={`selected-consent-${givenConsent.available_consent.uuid}`}
                      checked={selectedConsents.includes(givenConsent.available_consent.uuid)}
                      onChange={() => toggleSelectedConsent(givenConsent.available_consent.uuid)}
                      label={givenConsent.available_consent.content}
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
              (loadingConsents || selectedConsents.length === 0))
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
