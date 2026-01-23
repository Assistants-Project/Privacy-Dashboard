import { useEffect } from "react";
import { Button } from "react-bootstrap";
import { useAuth } from "./Authentication/AuthContext";
import { useNavigate } from "react-router-dom";
import { HomeModel } from "../../models/home";
import { Role, User } from "../../models/user";

function Home() {
  const auth = useAuth();
  const navigate = useNavigate();
  const homes = auth.user?.homes ?? [];
  const isDataSubject = auth.user?.role === Role.DataSubject;

  const renderOptional = (value: string | undefined) =>
    value && value.trim() ? value : <span className="muted">Non impostato</span>;

  const selectHome = (home: HomeModel) => {
    if (!auth.user) return;
    if (auth.user.current_home?.uuid === home.uuid) return;

    auth.setHome(
      new User(
        auth.user.email,
        auth.user.firstname,
        auth.user.lastname,
        auth.user.role,
        auth.user.homes,
      ),
      home
    );
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Privacy Dashboard</h1>
        <p>
          Benvenuto
          {auth.user ? `, ${auth.user.firstname} ${auth.user.lastname}` : ""}
        </p>
      </header>
      <main className="app-main">
        <section>
          <h2>Profilo utente</h2>
          {auth.user ? (
            <>
              <ul>
                <li>Email: {auth.user.email}</li>
                <li>Nome: {auth.user.firstname}</li>
                <li>Cognome: {auth.user.lastname}</li>
                <li>Ruolo: {auth.user.role}</li>
                {isDataSubject ? (
                  <li>
                    Casa corrente:{" "}
                    {auth.user.current_home?.name?.trim()
                      ? auth.user.current_home.name
                      : "Nessuna"}
                  </li>
                ) : null}
              </ul>

              {isDataSubject ? (
                <div className="mt-4">
                  <h2>Case</h2>
                  <p className="muted">
                    Clicca su una casa per impostarla come casa corrente.
                  </p>
                  {homes.length ? (
                    <div className="d-flex flex-nowrap gap-3 overflow-auto pb-2">
                      {homes.map((home, idx) => {
                        const isSelected =
                          auth.user?.current_home?.uuid === home.uuid ||
                          (!auth.user?.current_home && idx === 0);

                        return (
                          <button
                            key={home.uuid || idx}
                            type="button"
                            className={`card card-button ${isSelected ? "selected" : ""}`}
                            style={{ minWidth: 280 }}
                            onClick={() => selectHome(home)}
                          >
                            <div style={{ fontWeight: 700 }}>
                              {home.name?.trim()
                                ? home.name
                                : "Nome non impostato"}
                            </div>
                            <div className="muted" style={{ fontSize: 12 }}>
                              UUID:{" "}
                              {home.uuid?.trim() ? home.uuid : "Non impostato"}
                            </div>
                            <div className="kv-grid" style={{ marginTop: 12 }}>
                              <div className="kv-row">
                                <span>Address</span>
                                <span>{renderOptional(home.address)}</span>
                              </div>
                              <div className="kv-row">
                                <span>ZIP</span>
                                <span>{renderOptional(home.zip_code)}</span>
                              </div>
                              <div className="kv-row">
                                <span>Country</span>
                                <span>{renderOptional(home.country)}</span>
                              </div>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="card">
                      <div>Nessuna casa disponibile.</div>
                      <div className="muted">
                        La lista potrebbe essere vuota oppure non caricata.
                      </div>
                    </div>
                  )}
                </div>
              ) : null}

              <Button
                variant="secondary"
                onClick={() => navigate("/test-privacy-notice")}
                className="mt-3 ms-3"
              >
                Test Privacy Notice
              </Button>
              <Button
                variant="secondary"
                onClick={() => navigate("/test-privacy-impact-assessment")}
                className="mt-3 ms-3"
              >
                Test Privacy Impact Assessment
              </Button>
              <Button
                variant="secondary"
                onClick={() => navigate("/test-questionnaire")}
                className="mt-3 ms-3"
              >
                Test Questionnaire
              </Button>
              <Button
                variant="primary"
                onClick={() => navigate("/policy-translation")}
                className="mt-3 ms-3"
              >
                PTP (SIFIS)
              </Button>
            </>
          ) : (
            <p>Utente non disponibile. Effettua il login.</p>
          )}
        </section>
      </main>
    </div>
  );
}

export { Home };
