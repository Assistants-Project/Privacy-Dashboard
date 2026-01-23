import { useState } from 'react';
import { Alert, Button, Col, Container, Form, Row } from 'react-bootstrap';
import { Registration } from './Registration';
import { useAuth } from "./AuthContext";
import { Navigate } from "react-router-dom";
import './style.css';

function Login(props: any) {
    const auth = useAuth();
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("");

    if (auth.user) {
        return <Navigate to="/" replace />;
    }

    const handleSubmit = async (event: any) => {
        event.preventDefault();

        let valid = true;
        let msg = '';

        if (!email || email === '') {
            valid = false;
            msg += 'Please insert a valid username\r\n'
        }

        if (!password || password === '') {
            valid = false;
            msg += 'Please insert a valid password\r\n'
        }

        if (valid) {
            try {
                await auth.login(email, password); 
            } catch (err) {
                setError(err instanceof Error ? err.message : String(err))
            }
        }
        else {
            setError(msg)
        }
    }


    return (
        <Container fluid className="loginContainer">

            <Row className="loginTitle">
                <i className="bi bi-diagram-2">Privacy Dashboard</i>
            </Row>
            <Row>
                <Col>
                    <Row className="loginFormContainer">
                        <h2>Login</h2>
                        {error ? <Alert className="error" variant='danger' onClose={() => setError("")} dismissible>{error}</Alert> : false}
                        <Form.Group className="form" controlId='login'>
                            <Form.Control placeholder="Email" type='email' value={email} onChange={ev => setEmail(ev.target.value)} />
                            <Form.Control className="mt-3" placeholder="Password" type='password' value={password} onChange={ev => setPassword(ev.target.value)} />
                        </Form.Group>
                        <Button variant='warning' className='loginBtn' type='submit' onClick={handleSubmit}>LOGIN</Button>
                        <hr></hr>
                    </Row>
                </Col>
                <Col >
                    <Row className="loginFormContainer">
                        <Registration
                          registrationMessage={props.registrationMessage}
                          setRegistrationMessage={props.setRegistrationMessage}
                          setMessage={props.setMessage}
                          register={auth.registration}
                        />
                    </Row>
                </Col>
            </Row>

        </Container>
    )
}

export { Login }
