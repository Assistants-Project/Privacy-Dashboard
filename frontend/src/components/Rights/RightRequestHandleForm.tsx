import { useEffect, useState } from "react";
import { Button, Card, Form, Spinner } from "react-bootstrap";
import { RequestModel, RequestStatus } from "../../models/request";
import { handleRightRequest } from "../../services/RightsService";

type RightRequestHandleFormProps = {
  request: RequestModel;
  onSaved: () => Promise<void>;
};

function RightRequestHandleForm({ request, onSaved }: RightRequestHandleFormProps) {
  const [draftStatus, setDraftStatus] = useState<RequestStatus>(request.status);
  const [draftResponse, setDraftResponse] = useState<string>(
    request.response ?? "",
  );
  const [handling, setHandling] = useState<boolean>(false);
  const [errorHandling, setErrorHandling] = useState<string | undefined>(
    undefined,
  );

  //resetta il form quando cambia la request selezionata
  useEffect(() => {
    setDraftStatus(request.status);
    setDraftResponse(request.response ?? "");
    setHandling(false);
    setErrorHandling(undefined);
  }, [request.uuid]);

  const handleSave = async () => {
    setHandling(true);
    setErrorHandling(undefined);

    try {
      const trimmedResponse = draftResponse.trim();
      await handleRightRequest(
        request.uuid,
        request.application_uuid,
        draftStatus,
        trimmedResponse.length > 0 ? trimmedResponse : undefined,
      );
      await onSaved();
    } catch (err) {
      setErrorHandling(err instanceof Error ? err.message : "Errore inatteso");
    } finally {
      setHandling(false);
    }
  };

  return (
    <Card className="p-0">
      <Card.Body className="d-flex flex-column gap-3">
        {errorHandling ? (
          <Card bg="danger" text="white" className="p-0">
            <Card.Body>{errorHandling}</Card.Body>
          </Card>
        ) : undefined}

        <Form.Group controlId="handle-response">
          <Form.Label className="mb-1">Write a response</Form.Label>
          <Form.Control
            as="textarea"
            rows={4}
            placeholder="Write a response…"
            value={draftResponse}
            onChange={(e) => setDraftResponse(e.target.value)}
            disabled={handling}
          />
        </Form.Group>

        <Form.Group controlId="handle-status">
          <Form.Label className="mb-1">Status</Form.Label>
          <Form.Select
            value={draftStatus}
            onChange={(e) => setDraftStatus(e.target.value as RequestStatus)}
            disabled={handling}
          >
            <option value={RequestStatus.PENDING}>Pending</option>
            <option value={RequestStatus.HANDLED}>Handled</option>
          </Form.Select>
        </Form.Group>

        <Button variant="primary" onClick={handleSave} disabled={handling}>
          {handling ? (
            <span className="d-inline-flex align-items-center gap-2">
              <Spinner animation="border" size="sm" />
              Saving…
            </span>
          ) : (
            "Save"
          )}
        </Button>
      </Card.Body>
    </Card>
  );
}

export { RightRequestHandleForm };

