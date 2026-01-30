import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { Container, Navbar } from "react-bootstrap";
import { Login } from "./components/Authentication/Login";
import { useAuth } from "./components/Authentication/AuthContext";
import { TestPrivacyNotice } from "./components/GDPR/TestPrivacyNotice";
import { TestPrivacyImpactAssessment } from "./components/GDPR/TestPrivacyImpactAssessment";
import { TestQuestionnaire } from "./components/GDPR/TestQuestionnaire";
import { Home } from "./components/Home";
import PolicyTranslation from "./components/SIFIS/PolicyTranslation";
import { TopNavBar } from "./components/TopNavBar"
import { RequireAuth } from "./components/Authentication/RequireAuth";
import { Apps } from "./pages/Apps/Apps";

function PrivacyDashboard() {
  const auth = useAuth();

  return (
    <Container fluid style={{ padding: 0, height: "100%" }}>
      <Routes>

        <Route path="/login" element={<Login/>}/>

        <Route element={<RequireAuth><TopNavBar /></RequireAuth>}>

          <Route index element={<Home/>} />

          <Route
            path="/privacy-notice"
            element={
              <TestPrivacyNotice />
            }
          />

          <Route
            path="/installed-apps"
            element={
              <Apps />
            }
          />
          <Route
            path="/catalog"
            element={
              <Apps />
            }
          />

          <Route
            path="/privacy-impact-assessment"
            element={
              <TestPrivacyImpactAssessment/>
            }
          />
          <Route
            path="/questionnaire"
            element={
              <TestQuestionnaire/>
            }
          />
          <Route
            path="/policy-translation"
            element={
              <PolicyTranslation/>
            }
          />

        </Route>
      </Routes>
    </Container>
  );
}

export default PrivacyDashboard;
