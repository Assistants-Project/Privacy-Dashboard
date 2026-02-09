import { useState } from 'react';
import { Alert, Button, Card, Col, Container, Form, Row, Spinner } from 'react-bootstrap';
import { useAuth } from "../../contexts/AuthContext";
import { Navigate } from "react-router-dom";
import { Registration } from '../../components/Authentication/Registration';

function Login() {
    const auth = useAuth();
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("");
    const [waitingLogin, setWaitingLogin] = useState("");

    if (auth.user) {
        return <Navigate to="/" replace />;
    }

    const handleLogin = async (event: any) => {

        setError("");
        event.preventDefault();

        let valid = true;
        let msg = "";

        if (email === "") {
            valid = false;
            msg += "Please insert a valid email.\n"
        }

        if (password === "") {
            valid = false;
            msg += "Please insert a valid password.\n"
        }

        if (valid) {
            try {
                setWaitingLogin("Signing in... ");
                await auth.login(email, password);
            } catch (err) {
                setError(err instanceof Error ? err.message : String(err))
            }
            finally {
                setWaitingLogin("");
            }
        }
        else {
            setError(msg)
        }
    }


    return (
        <Container fluid className="min-vh-100 d-flex flex-column justify-content-center">

            <Row className="justify-content-center my-4">
                <Col xs="auto">
                    <h1>Privacy Dashboard</h1>
                </Col>
            </Row>
            <Row className="justify-content-center">
                <Col xs="auto" className="mx-3">
                    <Card>
                        <Card.Body>
                            <Card.Title>Login</Card.Title>
                            <Row className="justify-content-center mt-4">
                                <Col xs="auto">
                                    <Form onSubmit={handleLogin} className="d-flex flex-column gap-4">
                                        <Form.Group>
                                            <Form.Control placeholder="Email" type="email" value={email} onChange={ev => setEmail(ev.target.value)} />
                                            <Form.Control className="mt-3" placeholder="Password" type="password" value={password} onChange={ev => setPassword(ev.target.value)} />
                                        </Form.Group>
                                        <Button variant="secondary" className="align-self-center w-auto" type="submit" disabled={waitingLogin? true : false}>
                                            {waitingLogin ? waitingLogin : "Login"}
                                            {waitingLogin ? <Spinner animation="border" size="sm" /> : undefined}
                                                
                                        </Button>
                                    </Form>
                                </Col>
                            </Row>
                        </Card.Body>
                        {error ? <Alert variant='danger' onClose={() => setError("")} style={{ whiteSpace: "pre-line" }} dismissible>{error}</Alert> : undefined}
                    </Card>
                </Col>
                <Col xs="auto" className="mx-3">
                    <Registration/>
                </Col>
            </Row>
        </Container>
    )
}

export { Login }
