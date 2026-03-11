import { useEffect, useState } from "react";
import { Alert, Button, Form, Modal, Spinner } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { Role } from "../../models/user";

type UpdateProfileModalProps = { show: boolean; onHide: () => void; };

export function UpdateProfileModal({ show, onHide }: UpdateProfileModalProps) {
  const { user, updateProfile } = useAuth();
  const [currentPassword, setCurrentPassword] = useState("");
  const [email, setEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (!show) return;
    setCurrentPassword("");
    setEmail(user?.role === Role.DPO ? user.email : "");
    setNewPassword("");
    setSaving(false);
    setError(undefined);
  }, [show, user?.email, user?.role]);

  if (!user || user.role === Role.DataSubject) return null;

  const handleSubmit = async () => {
    setSaving(true);
    setError(undefined);

    try {
      await updateProfile({
        current_password: currentPassword,
        ...(user.role === Role.DPO && email.trim() !== user.email ? { email: email.trim() } : {}),
        ...(newPassword !== "" ? { new_password: newPassword } : {}),
      });
      onHide();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected Error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal show={show} onHide={saving ? undefined : onHide} centered>
      <Modal.Header closeButton={!saving}>
        <Modal.Title>{user.role === Role.DPO ? "Update email or password" : "Update password"}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form className="d-flex flex-column gap-3" onSubmit={(e) => { e.preventDefault(); void handleSubmit(); }}>
          {error ? <Alert variant="danger" className="mb-0">{error}</Alert> : undefined}
          {user.role === Role.DPO ? (
            <Form.Group controlId="update-profile-email">
              <Form.Label className="mb-1">New email</Form.Label>
              <Form.Control type="email" value={email} onChange={(e) => setEmail(e.target.value)} disabled={saving} />
            </Form.Group>
          ) : undefined}
          <Form.Group controlId="update-profile-current-password">
            <Form.Label className="mb-1">Current password</Form.Label>
            <Form.Control type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} disabled={saving} autoComplete="current-password" />
          </Form.Group>
          <Form.Group controlId="update-profile-new-password">
            <Form.Label className="mb-1">New password</Form.Label>
            <Form.Control type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} disabled={saving} autoComplete="new-password" placeholder={user.role === Role.DPO ? "Leave empty to keep the current password" : undefined} />
          </Form.Group>
          <div className="d-flex justify-content-end gap-2">
            <Button variant="outline-secondary" onClick={onHide} disabled={saving}>Cancel</Button>
            <Button type="submit" variant="primary" disabled={saving || currentPassword === "" || (user.role === Role.DPO ? email.trim() === user.email && newPassword === "" : newPassword === "")}>
              {saving ? <span className="d-inline-flex align-items-center gap-2"><Spinner animation="border" size="sm" />Saving…</span> : "Save"}
            </Button>
          </div>
        </Form>
      </Modal.Body>
    </Modal>
  );
}
