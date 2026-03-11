import { useEffect, useState } from "react";
import { Alert, Button, CloseButton, Form, InputGroup, Modal, Spinner } from "react-bootstrap";

import { useAuth } from "../../contexts/AuthContext";
import { useApp } from "../../contexts/AppsContext";
import { AppModel } from "../../models/app";
import { updateManagedApplicationByDataController } from "../../services/ApplicationService";

type AppCreationPanelProps = {
  show: boolean;
  onHide: () => void;
  mode?: "create" | "edit";
  application?: AppModel;
};

const MANUAL_APP_ID_PREFIX = "com.privacydashboard.";

function AppCreationPanel({ show, onHide, mode = "create", application }: AppCreationPanelProps) {
  const { user, isDataController } = useAuth();
  const { createManagedApplication, loadApps } = useApp();

  const [name, setName] = useState<string>("");
  const [title, setTitle] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [consentInput, setConsentInput] = useState<string>("");
  const [availableConsents, setAvailableConsents] = useState<string[]>([]);
  const [creating, setCreating] = useState<boolean>(false);
  const [error, setError] = useState<string | undefined>(undefined);
  const isEditMode = mode === "edit";

  useEffect(() => {
    if (!show) return;
    setName("");
    setTitle(isEditMode ? application?.title ?? "" : "");
    setDescription(isEditMode ? application?.description ?? "" : "");
    setConsentInput("");
    setAvailableConsents([]);
    setCreating(false);
    setError(undefined);
  }, [show, isEditMode, application?.uuid]);

  const handleAddConsent = () => {
    
    setError(undefined);
    const normalizedConsent = consentInput.trim();

    if (normalizedConsent === "") {
      return;
    }
    if (availableConsents.includes(normalizedConsent)) {
      setError("This consent is already in the list.");
      return;
    }

    setAvailableConsents((prev) => [...prev, normalizedConsent]);
    setConsentInput("");
  };

  const handleRemoveConsent = (index: number) => {
    setAvailableConsents((prev) => prev.filter((_, currentIndex) => currentIndex !== index));
  };

  const handleSubmit = async () => {

    setError(undefined);

    if (!user || !isDataController) {
      setError(`Only Data Controllers can ${isEditMode ? "edit" : "create"} applications.`);
      return;
    }

    const normalizedName = name.trim();
    const normalizedTitle = title.trim();
    const normalizedDescription = description.trim() === "" ? undefined : description.trim();
    const pendingConsent = consentInput.trim();
    const selectedConsents = [...availableConsents];

    if (pendingConsent !== "") {
      if (selectedConsents.includes(pendingConsent)) {
        setError("This consent is already in the list.");
        return;
      }
      selectedConsents.push(pendingConsent);
    }

    if (!isEditMode && normalizedName === "") {
      setError("Please provide an application id.");
      return;
    }
    if (normalizedTitle === "") {
      setError("Please provide an application title.");
      return;
    }

    setCreating(true);

    try {
      if (isEditMode) {
        if (!application) {
          setError("No application selected.");
          return;
        }
        await updateManagedApplicationByDataController(application.uuid, {
          title: normalizedTitle,
          description: normalizedDescription,
        });
        await loadApps(application.uuid, true);
      } else {
        await createManagedApplication({
          id: normalizedName,
          title: normalizedTitle,
          description: normalizedDescription,
          available_consents: selectedConsents.length > 0 ? selectedConsents : undefined,
        });
      }
      onHide();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected Error");
    } finally {
      setCreating(false);
    }
  };

  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>{isEditMode ? "Edit Application" : "Create Application"}</Modal.Title>
      </Modal.Header>

      <Modal.Body className="d-flex flex-column gap-3">
        {error ? <Alert variant="danger" className="mb-0">{error}</Alert> : undefined}

        {!isEditMode ? (
          <Form.Group>
            <Form.Label className="mb-1">ID(*)</Form.Label>
            <InputGroup>
              <InputGroup.Text>{MANUAL_APP_ID_PREFIX}</InputGroup.Text>
              <Form.Control
                type="text"
                placeholder="my-app"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={creating}
              />
            </InputGroup>
            <Form.Text className="text-muted">
              Only letters, numbers and '-' are allowed.
            </Form.Text>
          </Form.Group>
        ) : undefined}

        <Form.Group>
          <Form.Label className="mb-1">Title</Form.Label>
          <Form.Control
            type="text"
            placeholder="Application title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={creating}
          />
          <Form.Text className="text-muted">
            This is the name shown in the dashboard.
          </Form.Text>
        </Form.Group>

        <Form.Group>
          <Form.Label className="mb-1">Description</Form.Label>
          <Form.Control
            as="textarea"
            rows={4}
            placeholder="Short description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={creating}
          />
        </Form.Group>

        {!isEditMode ? (
          <>
            <Form.Group>
              <Form.Label className="mb-1">Available consents</Form.Label>
              <InputGroup>
                <Form.Control
                  type="text"
                  placeholder="Type a consent and press +"
                  value={consentInput}
                  onChange={(e) => setConsentInput(e.target.value)}
                  disabled={creating}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddConsent();
                    }
                  }}
                />
                <Button
                  variant="outline-primary"
                  onClick={handleAddConsent}
                  disabled={creating || consentInput.trim() === ""}
                >
                  +
                </Button>
              </InputGroup>
              <Form.Text className="text-muted">
                Add one or more consents that the Data Subject can grant to this app.
              </Form.Text>
            </Form.Group>

            {availableConsents.length > 0 ? (
              <div className="d-flex flex-column gap-2">
                {availableConsents.map((consent, index) => (
                  <div
                    key={`${consent}-${index}`}
                    className="d-inline-flex align-items-center justify-content-between border rounded px-2 py-1 bg-light"
                  >
                    <span>{consent}</span>
                    <CloseButton
                      onClick={() => handleRemoveConsent(index)}
                      disabled={creating}
                    />
                  </div>
                ))}
              </div>
            ) : undefined}
          </>
        ) : undefined}
      </Modal.Body>

      <Modal.Footer>
        <Button variant="outline-secondary" onClick={onHide} disabled={creating}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSubmit} disabled={creating}>
          {creating ? (
            <span className="d-inline-flex align-items-center gap-2">
              <Spinner animation="border" size="sm" />
              {isEditMode ? "Saving..." : "Creating..."}
            </span>
          ) : (
            isEditMode ? "Save Changes" : "Create Application"
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export { AppCreationPanel };
