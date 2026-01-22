import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { Container, Navbar } from "react-bootstrap";
import { Login } from "./Authentication/Login";
import { useUser } from "./Authentication/UserContext";
import { Role, User } from "../models/user";
import authentication from "./API/User/authentication";
import {
  getManagedApplications,
} from "./API/applicationAPI";
import { TestPrivacyNotice } from "./components/GDRP/TestPrivacyNotice";
import { TestPrivacyImpactAssessment } from "./components/GDRP/TestPrivacyImpactAssessment";
import { TestQuestionnaire } from "./components/GDRP/TestQuestionnaire";
import { Home } from "./components/Home";
import PolicyTranslation from "./components/SIFIS/PolicyTranslation";
import { TopNavBar } from "./components/TopNavBar"

function PrivacyDashboard() {
  const { user, setUser } = useUser();
  const navigate = useNavigate();
  const [registrationMessage, setRegistrationMessage] = useState("");
  const [loginMessage, setLoginMessage] = useState<String>("");

  //redirect user to the home page if a session is established
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const u = await authentication.getUserInfo();
        setUser(new User(u.email, u.firstname, u.lastname, u.role));
        console.log("User is authenticated, redirecting to home page.");
        navigate("/", { replace: true });
      } catch { }
    };
    checkAuth();
  }, []);

  const handleLogin = (email: string, password: string) => {
    setLoginMessage("");
    authentication
      .login(email, password)
      .then((u: User) => {
        setUser(new User(u.email, u.firstname, u.lastname, u.role));
        navigate("/", { replace: true });
      })
      .catch((err) => {
        //show login error from server
        const msg =
          err instanceof Error
            ? err.message
            : typeof err === "string"
              ? err
              : err?.error || err?.message || "An error occurred";
        setLoginMessage(msg);
      });
  };

  const handleRegister = (
    newUsername: string,
    name: string,
    surname: string,
    newPassword: string,
    role: string,
  ) => {
    // FAKE REGISTRATION
    console.debug("Registrazione utente", {
      newUsername,
      name,
      surname,
      role,
      newPassword,
    });
  };

  const doLogout = async () => {
    try {
      await authentication.logOut();
    } catch (err) {
      console.warn("Logout fallito", err);
    } finally {
      setUser(null);
      navigate("/login", { replace: true });
    }
  };

  const fetchManagedApplications = async () => {
    try {
      const applications = await getManagedApplications();
      return applications;
    } catch (err) {
      console.error("Error fetching managed applications:", err);
    }
  };

  return (
    <Container fluid style={{ padding: 0, height: "100%" }}>
      <Routes>

        <Route
          path="/login"
          element={
            <Login
              message={loginMessage}
              setMessage={setLoginMessage}
              registrationMessage={registrationMessage}
              setRegistrationMessage={setRegistrationMessage}
              login={handleLogin}
              register={handleRegister}
            />
          }
        />

        <Route

          element={user ? (<TopNavBar />) : (<Navigate to="/login" replace />)}>

          <Route index element={<Home onLogout={doLogout} />} />

          <Route
            path="/privacy-notice"
            element={
              <TestPrivacyNotice onLogout={doLogout} fetchManagedApplications={fetchManagedApplications} />
            }
          />
          <Route
            path="/privacy-impact-assessment"
            element={
              <TestPrivacyImpactAssessment onLogout={doLogout} fetchManagedApplications={fetchManagedApplications} />
            }
          />
          <Route
            path="/questionnaire"
            element={
              <TestQuestionnaire onLogout={doLogout} fetchManagedApplications={fetchManagedApplications} />
            }
          />
          <Route
            path="/policy-translation"
            element={
              <PolicyTranslation onLogout={doLogout} />
            }
          />

        </Route>
      </Routes>
    </Container>
  );
}

export default PrivacyDashboard;
