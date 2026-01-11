import { Button } from 'react-bootstrap';
import { useUser } from './Authentication/UserContext';
import { useNavigate } from 'react-router-dom';

type HomeProps = {
  onLogout: () => void;
};

function Home({ onLogout }: HomeProps) {
  const { user } = useUser();
  const navigate = useNavigate();

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Privacy Dashboard</h1>
        <p>Benvenuto{user ? `, ${user.firstname}` : ''}</p>
      </header>
      <main className="app-main">
        <section>
          <h2>Profilo utente</h2>
          {user ? (
            <>
              <ul>
                <li>Email: {user.email}</li>
                <li>Nome: {user.firstname}</li>
                <li>Cognome: {user.lastname}</li>
                <li>Ruolo: {user.role}</li>
              </ul>
              <Button variant="secondary" onClick={onLogout} className="mt-3">
                Logout
              </Button>
              <Button
                variant="secondary"
                onClick={() => navigate('/test-privacy-notice')}
                className="mt-3 ms-3"
              >
                Test Privacy Notice
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
