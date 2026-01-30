import { useAuth } from "./Authentication/AuthContext";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { Role } from "../models/user";
import { Container, Dropdown, Nav, Navbar, NavDropdown, Spinner } from "react-bootstrap";
import { UserMenu } from "./UserMenu";
import { useHome } from "./HomeContext";
import { useApp } from "./AppsContext";
import { ArrowRepeat } from 'react-bootstrap-icons';
import { CheckCircle } from 'react-bootstrap-icons';

export function TopNavBar() {

  const { user } = useAuth();
  const location = useLocation();
  const { current_home_uuid, updatingHomes, syncHomes } = useHome();
  const { updatingApps, syncApps } = useApp();

  const isDataSubject = user?.role === Role.DataSubject;
  const showQuestionnaire = !isDataSubject;


  const anySyncing = updatingHomes || updatingApps;

  const syncedIcon = (
    <CheckCircle className="text-success" style={{ width: 18, height: 18 }} />
  );
  const syncingIcon = (
    <Spinner animation="border" size="sm" />
  );

  const initials = [
    user?.firstname?.trim()?.[0],
    user?.lastname?.trim()?.[0],
  ]
    .filter(Boolean)
    .join("")
    .toUpperCase();

  return (
    <>
      <Navbar bg="light" variant="light" expand="lg" sticky="top" className="border-bottom">
        <Container fluid>
          <Nav className="align-items-center gap-2 flex-nowrap">
            <Navbar.Brand as={NavLink} to="/" end className="me-0">
              Privacy Dashboard {isDataSubject ? "|" : ""}
            </Navbar.Brand>
            {isDataSubject ? (
              <span className="text-muted text-nowrap">{current_home_uuid}</span>
            ) : undefined}
          </Nav>

          <Navbar.Toggle aria-controls="main-navbar" className="ms-auto" />

          <Navbar.Collapse id="main-navbar" className="w-100">

            <Nav
              className="flex-grow-1 justify-content-lg-center flex-nowrap gap-3 gap-lg-4"
              activeKey={location.pathname}
            >
              <Nav.Link as={NavLink} to="/" end eventKey="/">
                Home
              </Nav.Link>
              <Nav.Link as={NavLink} to="/privacy-notice" eventKey="/privacy-notice">
                Privacy Notice
              </Nav.Link>
              <Nav.Link
                as={NavLink}
                to={isDataSubject ? "/installed-apps" : "/catalog"}
                eventKey={isDataSubject ? "/installed-apps" : "/catalog"}
              >
                {isDataSubject ? "Installed Apps" : "Apps Catalog"}
              </Nav.Link>
              <Nav.Link
                as={NavLink}
                to="/privacy-impact-assessment"
                eventKey="/privacy-impact-assessment"
              >
                Privacy Impact Assessment
              </Nav.Link>
              {showQuestionnaire && (
                <Nav.Link as={NavLink} to="/questionnaire" eventKey="/questionnaire">
                  Questionnaire
                </Nav.Link>
              )}
              <Nav.Link as={NavLink} to="/policy-translation" eventKey="/policy-translation">
                Policy Translation
              </Nav.Link>
            </Nav>

            <Nav className="align-items-center gap-4">
              {isDataSubject ? (
                <NavDropdown
                  id="sync-dropdown"
                  align="end"
                  title={
                    <span
                      className="d-inline-flex align-items-center gap-2 border rounded px-2 py-1"
                      title={anySyncing ? "Sync in corso…" : "Sync completato"}
                    >
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
                  {/* <NavDropdown.Divider />
                  <NavDropdown.Header>Actions</NavDropdown.Header>
                  <NavDropdown.Item as="button">Sync Homes</NavDropdown.Item>
                  <NavDropdown.Item as="button" disabled>Sync Apps</NavDropdown.Item>
                  <NavDropdown.Item as="button" disabled>Sync All</NavDropdown.Item> */}
                </NavDropdown>
              ) : undefined}

              <Dropdown align="end" autoClose="outside">
                <Dropdown.Toggle
                  variant="outline-primary"
                  className="rounded-circle px-2 py-2 d-flex align-items-center justify-content-center"
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

      <Outlet />
    </>
  );
}
