import { useEffect, useState } from "react";
import { Alert, Button, Form, Modal, Spinner } from "react-bootstrap";

import { useAuth } from "../../contexts/AuthContext";
import { useApp } from "../../contexts/AppsContext";
import { Role } from "../../models/user";

type AppCreationPanelProps = {
  show: boolean;
  onHide: () => void;
};

function AppCreationPanel({ show, onHide }: AppCreationPanelProps) {
  const { user } = useAuth();
  const { createManagedApplication } = useApp();

  const [name, setName] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [creating, setCreating] = useState<boolean>(false);
  const [error, setError] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (!show) return;
    setName("");
    setDescription("");
    setCreating(false);
    setError(undefined);
  }, [show]);

  const handleCreate = async () => {

    setError(undefined);

    if (!user || user.role !== Role.DataController) {
      setError("Only Data Controllers can create applications.");
      return;
    }

    const normalizedName = name.trim();
    const normalizedDescription = description.trim() == ""? undefined : description.trim()

    if (normalizedName=="") {
      setError("Please provide an application name.");
      return;
    }

    setCreating(true);

    try {
      await createManagedApplication({name: normalizedName,description:normalizedDescription});
      onHide();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Errore inatteso");
    } finally {
      setCreating(false);
    }
  };

  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>Create application</Modal.Title>
      </Modal.Header>

      <Modal.Body className="d-flex flex-column gap-3">
        {error ? <Alert variant="danger" className="mb-0">{error}</Alert> : undefined}

        <Form.Group>
          <Form.Label className="mb-1">Name(*)</Form.Label>
          <Form.Control
            type="text"
            placeholder="Application name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={creating}
          />
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
      </Modal.Body>

      <Modal.Footer>
        <Button variant="outline-secondary" onClick={onHide} disabled={creating}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleCreate} disabled={creating}>
          {creating ? (
            <span className="d-inline-flex align-items-center gap-2">
              <Spinner animation="border" size="sm" />
              Creating…
            </span>
          ) : (
            "Create application"
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export { AppCreationPanel };
