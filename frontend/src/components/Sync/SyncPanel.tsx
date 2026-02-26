import { useEffect, useRef } from "react";
import { NavDropdown, Spinner } from "react-bootstrap";
import { ArrowRepeat, CheckCircle, ExclamationTriangleFill } from "react-bootstrap-icons";
import { useAuth } from "../../contexts/AuthContext";
import { useHome } from "../../contexts/HomeContext";
import { useApp } from "../../contexts/AppsContext";

export function SyncPanel() {
  const { loading, loginEventId, isDataSubject } = useAuth();
  const { updatingHomes, syncHomes, errorupdatingHomes } = useHome();
  const { updatingApps, syncApps, errorUpdatingApps } = useApp();
  const handledLoginEventIdRef = useRef(0);

  const anySyncing = updatingHomes || updatingApps;
  const anySyncError = !!errorupdatingHomes || !!errorUpdatingApps;

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
  const statusIcon = anySyncing ? syncingIcon : anySyncError ? errorIcon : syncedIcon;

  return (
    <NavDropdown id="sync-dropdown" align="end"
      title={
        <span
          className="d-inline-flex align-items-center gap-2 border rounded px-2 py-1"
          title={anySyncing ? "Syncing…" : anySyncError ? "Sync Failed" : "Sync Completed"}
        >
          <span>Smartotum Sync</span>
          {statusIcon}
        </span>
      }
    >
      <NavDropdown.Header>Sync Status</NavDropdown.Header>
      {anySyncError ? (
        <>
          {errorupdatingHomes ? (
            <NavDropdown.ItemText className="text-danger small">
              Homes Sync Failed
            </NavDropdown.ItemText>
          ) : undefined}
          {errorUpdatingApps ? (
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
        {updatingHomes ? syncingIcon : errorupdatingHomes ? errorIcon : syncedIcon}
        <span>Homes</span>
        <ArrowRepeat />
      </NavDropdown.Item>
      <NavDropdown.Item
        disabled={updatingApps}
        className="d-flex align-items-center gap-2"
        onClick={() => !updatingApps && syncApps()}
      >
        {updatingApps ? syncingIcon : errorUpdatingApps ? errorIcon : syncedIcon}
        <span>Apps</span>
        <ArrowRepeat />
      </NavDropdown.Item>
    </NavDropdown>
  );
}
