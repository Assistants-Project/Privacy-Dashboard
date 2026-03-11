import { useEffect, useRef, useState } from "react";
import { Alert, Modal, NavDropdown, Spinner } from "react-bootstrap";
import { ArrowRepeat, CheckCircle, ExclamationTriangleFill, InfoCircle } from "react-bootstrap-icons";
import { useAuth } from "../../contexts/AuthContext";
import { useHome } from "../../contexts/HomeContext";
import { useApp } from "../../contexts/AppsContext";

export function SyncPanel() {
  const { loading, loginEventId, isDataSubject } = useAuth();
  const { updatingHomes, syncHomes, homesSyncMessages } = useHome();
  const { updatingApps, syncApps, appsSyncMessages } = useApp();
  const handledLoginEventIdRef = useRef(0);
  const [showMessagesModal, setShowMessagesModal] = useState(false);

  const anySyncing = updatingHomes || updatingApps;
  const hasHomesSyncErrors = homesSyncMessages.some((message) => message.level === "error");
  const hasAppsSyncErrors = appsSyncMessages.some((message) => message.level === "error");
  const syncMessages = [...homesSyncMessages, ...appsSyncMessages];
  const hasSyncErrors = hasHomesSyncErrors || hasAppsSyncErrors;
  const hasSyncMessages = syncMessages.length > 0;
  const hasSyncWarningsOnly = hasSyncMessages && !hasSyncErrors;
  const anySyncError = hasSyncErrors;
  const warningColor = "#e0a800";
  const infoItemLabel = hasSyncErrors ? "Errors" : hasSyncMessages ? "Warning" : "Information";
  const infoItemStyle = hasSyncErrors ? undefined : hasSyncMessages ? { color: warningColor } : undefined;

  useEffect(() => {
    if (loading) return;
    if (!isDataSubject) return;
    if (loginEventId === 0) return;
    if (handledLoginEventIdRef.current === loginEventId) return;

    handledLoginEventIdRef.current = loginEventId;
    void (async () => {
      await syncHomes();
      await syncApps();
    })();
  }, [loading, isDataSubject, loginEventId, syncHomes, syncApps]);

  if (!isDataSubject) return null;

  const syncedIcon = (<CheckCircle className="text-success" style={{ width: 18, height: 18 }} />);
  const syncingIcon = <Spinner animation="border" size="sm" />;
  const errorIcon = (<ExclamationTriangleFill className="text-danger" style={{ width: 18, height: 18 }} />);
  const warningIcon = (<ExclamationTriangleFill style={{ width: 18, height: 18, color: warningColor }} />);
  const statusIcon = anySyncing ? syncingIcon : anySyncError ? errorIcon : hasSyncWarningsOnly ? warningIcon : syncedIcon;

  return (
    <>
      <NavDropdown id="sync-dropdown" align="end"
        title={
          <span
            className="d-inline-flex align-items-center gap-2 border rounded px-2 py-1"
            title={anySyncing ? "Syncing…" : anySyncError ? "Sync Failed" : hasSyncWarningsOnly ? "Sync Completed With Warnings" : "Sync Completed"}
          >
            <span>Smartotum Sync</span>
            {statusIcon}
          </span>
        }
      >
        <NavDropdown.Header>Sync Status</NavDropdown.Header>
        {anySyncError ? (
          <>
            {hasHomesSyncErrors ? (
              <NavDropdown.ItemText className="text-danger small">
                Homes Sync Failed
              </NavDropdown.ItemText>
            ) : undefined}
            {hasAppsSyncErrors ? (
              <NavDropdown.ItemText className="text-danger small">
                Apps Sync Failed
              </NavDropdown.ItemText>
            ) : undefined}
            <NavDropdown.Divider />
          </>
        ) : undefined}
        <NavDropdown.Item
          disabled={updatingHomes}
          className="d-flex align-items-center gap-2"
          onClick={() => !updatingHomes && syncHomes()}
        >
          {updatingHomes ? syncingIcon : hasHomesSyncErrors ? errorIcon : syncedIcon}
          <span>Homes</span>
          <ArrowRepeat />
        </NavDropdown.Item>
        <NavDropdown.Item
          disabled={updatingApps}
          className="d-flex align-items-center gap-2"
          onClick={() => !updatingApps && syncApps()}
        >
          {updatingApps ? syncingIcon : hasAppsSyncErrors ? errorIcon : syncedIcon}
          <span>Apps</span>
          <ArrowRepeat />
        </NavDropdown.Item>
        <NavDropdown.Divider />
        <NavDropdown.Item
          disabled={!hasSyncMessages}
          className={hasSyncErrors ? "d-flex align-items-center gap-2 text-danger" : "d-flex align-items-center gap-2"}
          style={infoItemStyle}
          onClick={() => hasSyncMessages && setShowMessagesModal(true)}
        >
          <InfoCircle />
          <span>{infoItemLabel}</span>
        </NavDropdown.Item>
      </NavDropdown>

      <Modal show={showMessagesModal} onHide={() => setShowMessagesModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Synchronization Log</Modal.Title>
        </Modal.Header>
        <Modal.Body className="d-flex flex-column gap-3">
          {syncMessages.map((message, index) => (
            <Alert key={`${message.level}-${message.text}-${index}`} variant={message.level === "error" ? "danger" : "warning"} className="mb-0">
              {message.text}
            </Alert>
          ))}
        </Modal.Body>
      </Modal>
    </>
  );
}
