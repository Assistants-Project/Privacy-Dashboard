import { useAuth } from "./Authentication/AuthContext";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { Role } from "../models/user";
import { Button, Container, Dropdown, Nav, Navbar } from "react-bootstrap";
import { UserMenu } from "./UserMenu";

export function TopNavBar() {

  const { user } = useAuth();
  const location = useLocation();

  const showQuestionnaire =
    user?.role === Role.DatController || user?.role === Role.DPO;

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
          <Navbar.Brand as={NavLink} to="/" end>
            Privacy Dashboard
          </Navbar.Brand>

          <Navbar.Toggle aria-controls="main-navbar" />
          <Navbar.Collapse id="main-navbar" className="w-100">

            <Nav
              className="mx-lg-auto justify-content-lg-center flex-nowrap gap-3 gap-lg-4"
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
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Outlet />
    </>
  );
}
