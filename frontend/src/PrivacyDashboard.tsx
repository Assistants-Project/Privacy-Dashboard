import { Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Container } from 'react-bootstrap';
import { Login } from './Authentication/Login';
import { useUser } from './Authentication/UserContext';
import { Role, User } from '../models/user';
import authentication from '../API/User/authentication'
import { Home } from './Home';

function PrivacyDashboard() {

  const { user, setUser } = useUser();
  const navigate = useNavigate();
  const [registrationMessage, setRegistrationMessage] = useState('');
  const [loginMessage, setLoginMessage] = useState<String>('');


  //redirect user to the home page if a session is established
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const u = await authentication.getUserInfo()
        setUser(new User(u.email, u.firstname, u.lastname, u.role));
        navigate('/', { replace: true });
      } catch {
      }
    };
    checkAuth();
  }, []);

  const handleLogin = (email: string, password: string) => {
    setLoginMessage('');
    authentication.login(email, password)
      .then((u: User) => {
        setUser(new User(u.email, u.firstname, u.lastname, u.role))
        navigate('/', { replace: true });
      })
      .catch(err => {
        //show login error from server
        const msg = err instanceof Error ? err.message : typeof err === 'string' ? err : (err?.error || err?.message || 'An error occurred');
        setLoginMessage(msg);
      })
  };

  const handleRegister = (
    newUsername: string,
    name: string,
    surname: string,
    newPassword: string,
    role: string,
  ) => {
    // FAKE REGISTRATION
    console.debug('Registrazione utente', { newUsername, name, surname, role, newPassword });
  };

  const doLogout = async () => {
    try {
      await authentication.logOut();
    } catch (err) {
      console.warn('Logout fallito', err);
    } finally {
      setUser(null);
      navigate('/login', { replace: true });
    }
  };

  return (
    <Container fluid style={{ padding: 0, height: "100%" }}>
      <Routes>


        <Route path="/" element={user ? <Home onLogout={doLogout} /> : <Navigate to="/login" replace />} />

        <Route path="/login"
          element={
              <Login
                message={loginMessage}
                setMessage={setLoginMessage}
                registrationMessage={registrationMessage}
                setRegistrationMessage={setRegistrationMessage}
                login={handleLogin}
                register={handleRegister}
              />
          }
        />
      </Routes>
    </Container>
  );
}

export default PrivacyDashboard;
