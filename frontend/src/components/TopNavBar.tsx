import React, { useEffect, useState } from "react";
import { useAuth } from "../Authentication/AuthContext";
import { NavLink, Outlet } from "react-router-dom";
import { Role } from "../../models/user";
import Button from "react-bootstrap/esm/Button";

export function TopNavBar() {

    const { user, logout } = useAuth();

    const navLinkClassName = ({ isActive }: { isActive: boolean }) =>
    isActive ? "active" : undefined;

    const showQuestionnaire =
    user?.role === Role.DatController || user?.role === Role.DPO;
  

  useEffect(() => {
    //  <div className="userbox">
    //         <UserMenu />
    //       </div>
   
  }, []);

  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <NavLink to="/">Privacy Dashboard</NavLink>
          </div>
          <nav className="nav">
            <NavLink className={navLinkClassName} to="/privacy-notice">
              Privacy Notice
            </NavLink>
            <NavLink className={navLinkClassName} to="/privacy-impact-assessment">
              Privacy Impact Assessment
            </NavLink>
            <NavLink className={navLinkClassName} to="/questionnaire">
              Questionnaire
            </NavLink>
            <NavLink className={navLinkClassName} to="/policy-translation">
              Policy Translation
            </NavLink>
            <NavLink className={navLinkClassName} to="/login">
              <Button onClick={logout}>Logout</Button>
            </NavLink>
          </nav>
        </div>
      </header>
      <Outlet />
    </>
  );
}
