import { useEffect, useMemo, useState } from "react";
import { Button, Form, Modal, Spinner } from "react-bootstrap";
import { useApp } from "../../contexts/AppsContext";
import { useAuth } from "../../contexts/AuthContext";
import { DocumentStatus } from "../../models/app";
import { handleReplacePrivacyNoticeWithExisting } from "../../services/PrivacyNoticeService";
import { PrivacyNoticeHtmlPreview } from "./PrivacyNoticeHtmlPreview";

type Props = { show: boolean; onHide: () => void };

function ApplyExistingPrivacyNoticeModal({ show, onHide }: Props) {
  const { user, isDataSubject } = useAuth();
  const { apps, selectedApp, selectedAppUUID, PrivacyNoticeByAppUUID, loadPrivacyNotice } = useApp();

  const sourceApps = useMemo(() => {
    if (!apps) return [];
    return apps.filter((a) => a && a.uuid !== selectedAppUUID && a.pn_status === DocumentStatus.Available);
  }, [apps, selectedAppUUID]);

  const [sourceAppUuid, setSourceAppUuid] = useState("");
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [applying, setApplying] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);

  const sourcePn = sourceAppUuid ? PrivacyNoticeByAppUUID[sourceAppUuid] : undefined;
  const missingPreview = !!(show && sourceAppUuid && sourcePn === undefined);

  useEffect(() => {
    if (!show) return;
    setError(undefined);
    setApplying(false);
    setLoadingPreview(false);
    setSourceAppUuid((prev) => {
      if (prev && sourceApps.some((a) => a.uuid === prev)) return prev;
      return sourceApps[0]?.uuid ?? "";
    });
  }, [show, sourceApps]);

  useEffect(() => {
    if (!show) return;
    if (!sourceAppUuid) return;
    if (PrivacyNoticeByAppUUID[sourceAppUuid] !== undefined) {
      // Avoid refetching in the modal: it causes a noticeable preview flicker.
      return;
    }
    setLoadingPreview(true);
    setError(undefined);
    loadPrivacyNotice(sourceAppUuid, true)
      .catch((e) => {
        setError(e instanceof Error ? e.message : "Unexpected error");
      })
      .finally(() => setLoadingPreview(false));
  }, [show, sourceAppUuid, loadPrivacyNotice]);

  const onApply = async () => {
    if (!user || isDataSubject) return;
    if (!selectedAppUUID) return;
    if (!sourcePn || !sourcePn.uuid) {
      setError("Select an application with a Privacy Notice");
      return;
    }

    setApplying(true);
    setError(undefined);
    try {
      await handleReplacePrivacyNoticeWithExisting(selectedAppUUID, sourcePn.uuid);
      await loadPrivacyNotice(selectedAppUUID, true); // keep cache/status in sync
      onHide();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unexpected error");
    } finally {
      setApplying(false);
    }
  };

  const targetTitle = selectedApp?.name ?? "";

  return (
    <Modal show={show} onHide={onHide} centered size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Apply existing Privacy Notice</Modal.Title>
      </Modal.Header>
      <Modal.Body className="d-flex flex-column gap-3">
        <div className="small text-muted">Target application: {targetTitle || "(none selected)"}</div>

        <Form.Group className="mb-0">
          <Form.Label className="small text-muted">Source application</Form.Label>
          <Form.Select
            value={sourceAppUuid}
            disabled={applying || sourceApps.length === 0}
            onChange={(e) => setSourceAppUuid(e.target.value)}
          >
            {sourceApps.length === 0 ? (
              <option value="">No applications Privacy Notice found</option>
            ) : (
              sourceApps.map((a) => (
                <option key={a.uuid} value={a.uuid}>
                  {a.title || a.name}
                </option>
              ))
            )}
          </Form.Select>
        </Form.Group>

        <div>
          <div className="small text-muted mb-1">Preview</div>
          <PrivacyNoticeHtmlPreview
            content={sourcePn?.content}
            loading={loadingPreview || missingPreview}
            emptyText="No preview available"
            maxHeight="45vh"
          />
        </div>

        {error ? <div className="text-danger small">{error}</div> : undefined}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="outline-secondary" onClick={onHide} disabled={applying}>
          Cancel
        </Button>
        <Button variant="primary" onClick={onApply} disabled={applying || !selectedAppUUID || !sourceAppUuid}>
          {applying ? (
            <span className="d-inline-flex align-items-center gap-2">
              <Spinner animation="border" size="sm" />
              Applying…
            </span>
          ) : (
            "Apply"
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export { ApplyExistingPrivacyNoticeModal };
