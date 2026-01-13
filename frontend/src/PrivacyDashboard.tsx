import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { Container } from "react-bootstrap";
import { Login } from "./Authentication/Login";
import { useUser } from "./Authentication/UserContext";
import { Role, User } from "../models/user";
import authentication from "../API/User/authentication";
import {
  getManagedApplications,
  getPiaTemplate,
  getPiaByManagedApplicationUuid,
  submitPiaByManagedApplicationUuid,
} from "../API/applicationAPI";
import {
  getPrivacyNoticeTemplate,
  getPrivacyNoticeByManagedApplicationUuid,
  writePrivacyNoticeByManagedApplicationUuid,
  removePrivacyNoticeByManagedApplicationUuid,
} from "../API/privacyNoticeAPI";
import { TestPrivacyNotice } from "./TestPrivacyNotice";
import { TestPrivacyImpactAssessment } from "./TestPrivacyImpactAssessment";
import { Home } from "./Home";

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
      } catch {}
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
    role: string
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

  const fetchPrivacyNoticeTemplate = async () => {
    try {
      console.log("Trying to get Privacy Notice Template");
      const result = await getPrivacyNoticeTemplate();
      console.log("Privacy Notice Template retrieved successfully: ", result);
      return result;
    } catch (err) {
      console.error("Error getting privacy notice template:", err);
    }
  };

  const handleGetPrivacyNotice = async (applicationUuid: string) => {
    try {
      console.log(
        "Trying to get Privacy Notice for application: ",
        applicationUuid
      );
      const result = await getPrivacyNoticeByManagedApplicationUuid(
        applicationUuid
      );
      console.log("Privacy Notice retrieved successfully: ", result);
      return result;
    } catch (err) {
      console.error("Error getting privacy notice:", err);
    }
  };

  const handleSubmitPrivacyNotice = async (
    applicationUuid: string,
    privacyNoticeContent: string
  ) => {
    try {
      console.log(
        "Trying to submit Privacy Notice to application: ",
        applicationUuid,
        privacyNoticeContent
      );
      const result = await writePrivacyNoticeByManagedApplicationUuid(
        applicationUuid,
        privacyNoticeContent
      );
      console.log("Privacy Notice submitted successfully: ", result);
      return result;
    } catch (err) {
      console.error("Error submitting privacy notice:", err);
    }
  };

  const handleRemovePrivacyNotice = async (applicationUuid: string) => {
    try {
      console.log(
        "Trying to delete existing privacy notice for application: ",
        applicationUuid
      );
      await removePrivacyNoticeByManagedApplicationUuid(applicationUuid);
      console.log("Existing privacy notice deleted.");
    } catch (err) {
      console.error("Error deleting privacy notice:", err);
    }
  };

  const fetchPiaTemplate = async () => {
    try {
      console.log("Trying to get Privacy Impact Assessment Template");
      const result = await getPiaTemplate();
      console.log("Privacy Impact Assessment Template retrieved successfully");
      return result;
    } catch (err) {
      console.error("Error getting privacy impact assessment template:", err);
    }
  };

  const handleGetPrivacyImpactAssessment = async (applicationUuid: string) => {
    try {
      console.log(
        "Trying to get Privacy Impact Assessment for application: ",
        applicationUuid
      );
      const result = await getPiaByManagedApplicationUuid(applicationUuid);
      console.log("Privacy Impact Assessment retrieved successfully");
      return result;
    } catch (err) {
      console.error("Error getting privacy impact assessment:", err);
    }
  };

  const submitPiaTemplate = async (
    applicationUuid: string,
    piaTemplate: any
  ) => {
    try {
      await submitPiaByManagedApplicationUuid(applicationUuid, piaTemplate);
      console.log("Privacy Impact Assessment submitted successfully");
      return;
    } catch (err) {
      console.error("Error submitting privacy impact assessment:", err);
    }
  };

  return (
    <Container fluid style={{ padding: 0, height: "100%" }}>
      <Routes>
        <Route
          path="/"
          element={
            user ? (
              <Home onLogout={doLogout} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

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
          path="/test-privacy-notice"
          element={
            user ? (
              <TestPrivacyNotice
                onLogout={doLogout}
                fetchPrivacyNoticeTemplate={fetchPrivacyNoticeTemplate}
                fetchManagedApplications={fetchManagedApplications}
                handleGetPrivacyNotice={handleGetPrivacyNotice}
                handleSubmitPrivacyNotice={handleSubmitPrivacyNotice}
                handleRemovePrivacyNotice={handleRemovePrivacyNotice}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/test-privacy-impact-assessment"
          element={
            user ? (
              <TestPrivacyImpactAssessment
                onLogout={doLogout}
                fetchPiaTemplate={fetchPiaTemplate}
                fetchManagedApplications={fetchManagedApplications}
                handleGetPrivacyImpactAssessment={
                  handleGetPrivacyImpactAssessment
                }
                submitPiaTemplate={submitPiaTemplate}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </Container>
  );
}

export default PrivacyDashboard;
