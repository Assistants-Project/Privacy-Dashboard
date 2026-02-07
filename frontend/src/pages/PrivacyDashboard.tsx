import { Navigate, Route, Routes } from "react-router-dom";
import { Container } from "react-bootstrap";
import { Login } from "./Authentication/Login";
import { useAuth } from "../contexts/AuthContext";
import { Questionnaire } from "./Questionnaire/Questionnaire";
import PolicyTranslation from "./PolicyTranslation/PolicyTranslation";
import { TopNavBar } from "../components/Routing/TopNavBar";
import { RequireAuth } from "../components/Routing/RequireAuth";
import { Apps } from "./Apps/Apps";
import { Messages } from "./Messages/Messages";
import { ManageRights } from "./RightsRequest/ManageRights";
import { Role } from "../models/user";
import { Home } from "./Home";
import { PrivacyNotice } from "./PrivacyNotice/PrivacyNotice";
import { PrivacyImpactAssessment } from "./PIA/PrivacyImpactAssessment";

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
