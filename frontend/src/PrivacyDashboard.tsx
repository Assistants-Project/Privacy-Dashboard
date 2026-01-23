import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { Container, Navbar } from "react-bootstrap";
import { Login } from "./Authentication/Login";
import { useAuth } from "./Authentication/AuthContext";
import { TestPrivacyNotice } from "./components/GDRP/TestPrivacyNotice";
import { TestPrivacyImpactAssessment } from "./components/GDRP/TestPrivacyImpactAssessment";
import { TestQuestionnaire } from "./components/GDRP/TestQuestionnaire";
import { Home } from "./components/Home";
import PolicyTranslation from "./components/SIFIS/PolicyTranslation";
import { TopNavBar } from "./components/TopNavBar"

function PrivacyDashboard() {
  const auth = useAuth();

  return (
    <Container fluid style={{ padding: 0, height: "100%" }}>
      <Routes>

        <Route
          path="/login"
          element={
            auth.user ? (
              <Navigate to="/" replace />
            ) : (
              <Login/>
            )
          }
        />

        <Route

          element={auth.user ? (<TopNavBar />) : (<Navigate to="/login" replace />)}>

          <Route index element={<Home/>} />

          <Route
            path="/privacy-notice"
            element={
              <TestPrivacyNotice />
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
