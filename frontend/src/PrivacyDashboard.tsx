import { Navigate, Route, Routes } from "react-router-dom";
import { Container } from "react-bootstrap";
import { Login } from "./components/Authentication/Login";
import { useAuth } from "./components/Authentication/AuthContext";
import { PrivacyNotice } from "./components/GDPR/PrivacyNotice";
import { PrivacyImpactAssessment } from "./components/GDPR/PrivacyImpactAssessment";
import { Questionnaire } from "./components/GDPR/Questionnaire";
import { Home } from "./components/Home";
import PolicyTranslation from "./components/SIFIS/PolicyTranslation";
import { TopNavBar } from "./components/TopNavBar";
import { RequireAuth } from "./components/Authentication/RequireAuth";
import { Apps } from "./pages/Apps/Apps";
import { Messages } from "./pages/Messages/Messages";
import { ManageRights } from "./pages/ManageRights";
import { Role } from "./models/user";

function PrivacyDashboard() {
  const auth = useAuth();
  const isDataSubject = auth.user?.role === Role.DataSubject;

  return (
    <Container
      fluid
      style={{
        padding: 0,
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route
          element={
            <RequireAuth>
              <TopNavBar />
            </RequireAuth>
          }
        >
          <Route index element={<Home />} />

          <Route path="/privacy-notice" element={<PrivacyNotice />} />

          <Route path="/installed-apps" element={<Apps />} />
          <Route path="/catalog" element={<Apps />} />

          <Route
            path="/privacy-impact-assessment"
            element={
              isDataSubject ? (
                <Navigate to="/" replace />
              ) : (
                <PrivacyImpactAssessment />
              )
            }
          />
          <Route path="/questionnaire" element={<Questionnaire />} />
          <Route path="/policy-translation" element={<PolicyTranslation />} />
          <Route path="/messages" element={<Messages />} />
          <Route path="/rights" element={<ManageRights />} />
        </Route>
      </Routes>
    </Container>
  );
}

export default PrivacyDashboard;
