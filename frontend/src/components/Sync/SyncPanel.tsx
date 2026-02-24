import { useEffect, useRef } from "react";
import { NavDropdown, Spinner } from "react-bootstrap";
import { ArrowRepeat, CheckCircle } from "react-bootstrap-icons";
import { useAuth } from "../../contexts/AuthContext";
import { useHome } from "../../contexts/HomeContext";
import { useApp } from "../../contexts/AppsContext";
import { Role } from "../../models/user";

export function SyncPanel() {
  const { user, loading, loginEventId } = useAuth();
  const { updatingHomes, syncHomes } = useHome();
  const { updatingApps, syncApps } = useApp();
  const handledLoginEventIdRef = useRef(0);

  const isDataSubject = user?.role === Role.DataSubject;
  const anySyncing = updatingHomes || updatingApps;

  useEffect(() => {
    if (loading) return;
    if (user?.role !== Role.DataSubject) return;
    if (loginEventId === 0) return;
    if (handledLoginEventIdRef.current === loginEventId) return;

    handledLoginEventIdRef.current = loginEventId;
    void (async () => {
      await syncHomes();
      await syncApps();
    })();
  }, [loading, user?.uuid, user?.role, loginEventId, syncHomes, syncApps]);

  if (!isDataSubject) return null;

  const syncedIcon = (<CheckCircle className="text-success" style={{ width: 18, height: 18 }} />);
  const syncingIcon = <Spinner animation="border" size="sm" />;

  return (
    <NavDropdown id="sync-dropdown" align="end"
      title={
        <span className="d-inline-flex align-items-center gap-2 border rounded px-2 py-1" title={anySyncing ? "Sync in corso…" : "Sync completato"}>
          <span>Smartotum Sync</span>
          {anySyncing ? syncingIcon : syncedIcon}
        </span>
      }
    >
      <NavDropdown.Header>Sync Status</NavDropdown.Header>
      <NavDropdown.Item
        disabled={updatingHomes}
        className="d-flex align-items-center gap-2"
        onClick={() => !updatingHomes && syncHomes()}
      >
        {updatingHomes ? syncingIcon : syncedIcon}
        <span>Homes</span>
        <ArrowRepeat />
      </NavDropdown.Item>
      <NavDropdown.Item
        disabled={updatingApps}
        className="d-flex align-items-center gap-2"
        onClick={() => !updatingApps && syncApps()}
      >
        {updatingApps ? syncingIcon : syncedIcon}
        <span>Apps</span>
        <ArrowRepeat />
      </NavDropdown.Item>
    </NavDropdown>
  );
}
