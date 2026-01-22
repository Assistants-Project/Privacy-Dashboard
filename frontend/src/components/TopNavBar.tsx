import React, { useEffect, useState } from "react";
import { useUser } from "../Authentication/UserContext";
import { NavLink, Outlet } from "react-router-dom";
import { Role } from "../../models/user";

export function TopNavBar() {

    const { user } = useUser();

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
          </nav>
        </div>
      </header>
      <Outlet />
    </>
  );
}
