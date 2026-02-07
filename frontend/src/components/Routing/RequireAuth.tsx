import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const auth = useAuth();
  const location = useLocation();

  if (auth.loading) {
    return (
      <div className="container">
        <div className="card">Loading…</div>
      </div>
    );
  }

  if (!auth.user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <>{children}</>;
}
