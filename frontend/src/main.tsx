import React from 'react';
import ReactDOM from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter } from 'react-router-dom';
import PrivacyDashboard from './PrivacyDashboard';
import { UserProvider } from './Authentication/UserContext';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <UserProvider>
        <PrivacyDashboard />
      </UserProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
