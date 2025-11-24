import { Button } from 'react-bootstrap';
import { useUser } from './Authentication/UserContext';

type HomeProps = {
  onLogout: () => void;
};

function Home({ onLogout }: HomeProps) {
  const { user } = useUser();

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
            </>
          ) : (
            <p>Utente non disponibile. Effettua il login.</p>
          )}
        </section>
      </main>
    </div>
  );
}

export { Home }
