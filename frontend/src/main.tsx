import React from "react";
import ReactDOM from "react-dom/client";
import "bootstrap/dist/css/bootstrap.min.css";
import "./style.css"
import { BrowserRouter } from "react-router-dom";
import { AllCommunityModule, ModuleRegistry } from "ag-grid-community";
import PrivacyDashboard from "./PrivacyDashboard";
import { AuthProvider } from "./components/Authentication/AuthContext";

ModuleRegistry.registerModules([AllCommunityModule]);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <PrivacyDashboard />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
