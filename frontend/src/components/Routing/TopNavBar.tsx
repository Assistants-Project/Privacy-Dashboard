import { useEffect, useRef, useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { Role } from "../../models/user";
import {Container,Dropdown,Nav,Navbar} from "react-bootstrap";
import { UserMenu } from "../Authentication/UserMenu";
import { useHome } from "../../contexts/HomeContext";
import { SyncPanel } from "../Sync/SyncPanel";
import { useApp } from "../../contexts/AppsContext";

export function TopNavBar() {
  const { user } = useAuth();
  const location = useLocation();
  const { current_home_uuid, updatingHomes } = useHome();
  const { updatingApps } = useApp();
  const [showSyncCompleted, setShowSyncCompleted] = useState(false);
  const wasSyncingRef = useRef(false);

  const isDataSubject = user?.role === Role.DataSubject;
  const showQuestionnaire = !isDataSubject;
  const anySyncing = isDataSubject && (updatingHomes || updatingApps);

  const initials = [user?.firstname?.trim()?.[0], user?.lastname?.trim()?.[0]].filter(Boolean).join("").toUpperCase();

  useEffect(() => {
    const wasSyncing = wasSyncingRef.current;
    wasSyncingRef.current = anySyncing;

    if (!isDataSubject) return;
    if (wasSyncing && !anySyncing) {
      setShowSyncCompleted(true);
      const timeoutId = window.setTimeout(() => setShowSyncCompleted(false), 2400);
      return () => window.clearTimeout(timeoutId);
    }
  }, [anySyncing, isDataSubject]);

  return (
    <div className="app-shell">
      <Navbar variant="light" expand="lg"
        className="border-bottom shadow-sm flex-shrink-0 py-0">
        <Container fluid className="h-100">
          <Nav className="align-items-center gap-2 flex-nowrap">
            <Navbar.Brand as={NavLink} to="/" end className="me-0">
              Privacy Dashboard {isDataSubject ? "|" : ""}
            </Navbar.Brand>
            {isDataSubject ? (
              <span className="text-muted text-nowrap">
                {current_home_uuid}
              </span>
            ) : undefined}
          </Nav>

          <Navbar.Toggle aria-controls="main-navbar" className="ms-auto" />

          <Navbar.Collapse id="main-navbar" className="w-100 h-100">
            <Nav className="flex-grow-1 justify-content-lg-center flex-nowrap gap-3 gap-lg-4 h-100"
              activeKey={location.pathname}
            >
              <Nav.Link as={NavLink} to="/" end eventKey="/" className="d-flex align-items-center">
                Home
              </Nav.Link>
               <Nav.Link as={NavLink} to="/installed-apps" eventKey="/installed-apps" className="d-flex align-items-center">
                {isDataSubject ? "Installed Apps" : "Managed Apps"}
              </Nav.Link>
              <Nav.Link as={NavLink} to="/privacy-notice" eventKey="/privacy-notice" className="d-flex align-items-center">
                Privacy Notice
              </Nav.Link>
              {!isDataSubject && (
                <Nav.Link as={NavLink} to="/privacy-impact-assessment" eventKey="/privacy-impact-assessment" className="d-flex align-items-center">
                  Privacy Impact Assessment
                </Nav.Link>
              )}
              {showQuestionnaire && (
                <Nav.Link as={NavLink} to="/questionnaire" eventKey="/questionnaire" className="d-flex align-items-center">
                  Questionnaire
                </Nav.Link>
              )}
              {isDataSubject &&
                <Nav.Link as={NavLink} to="/policy-translation" eventKey="/policy-translation" className="d-flex align-items-center">
                  Policy Translation
                </Nav.Link>
              }
              <Nav.Link as={NavLink} to="/rights" eventKey="/rights" className="d-flex align-items-center">
                {isDataSubject ? "Rights Request" : "Rights Request"}
              </Nav.Link>

              <Nav.Link as={NavLink} to="/messages" eventKey="/messages" className="d-flex align-items-center">
                Messages
              </Nav.Link>
            </Nav>

            <Nav className="align-items-center gap-4 position-relative">
              {isDataSubject && showSyncCompleted ? (
                <span
                  aria-live="polite"
                  className="p-2 position-absolute top-50 end-100 translate-middle-y badge rounded-pill text-bg-success me-3"
                >
                  Sync Completed!
                </span>
              ) : undefined}

              <SyncPanel />


              <Dropdown align="end" autoClose="outside">
                <Dropdown.Toggle
                  variant="light"
                  className="rounded-circle d-inline-flex align-items-center justify-content-center p-0 border border-dark-subtle text-dark bg-body-tertiary shadow-sm fw-semibold"
                  style={{ width: 39, height: 38, lineHeight: 1, fontSize: "0.90rem" }}
                >
                  {initials || "U"}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <UserMenu />
                </Dropdown.Menu>
              </Dropdown>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container fluid className="mx-auto app-shell-content py-2" style={{maxWidth: 1800}}>
        <Outlet />
      </Container>
    </div>
  );
}
