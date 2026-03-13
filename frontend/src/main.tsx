import React from "react";
import ReactDOM from "react-dom/client";
import "bootstrap/dist/css/bootstrap.min.css";
import "./style.css"
import { BrowserRouter } from "react-router-dom";
import { AllCommunityModule, ModuleRegistry } from "ag-grid-community";
import PrivacyDashboard from "./pages/PrivacyDashboard";
import { AuthProvider } from "./contexts/AuthContext";
import { HomeProvider } from "./contexts/HomeContext";
import { AppsProvider } from "./contexts/AppsContext";

ModuleRegistry.registerModules([AllCommunityModule]);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <HomeProvider>
          <AppsProvider>
            <PrivacyDashboard />
          </AppsProvider>
        </HomeProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
