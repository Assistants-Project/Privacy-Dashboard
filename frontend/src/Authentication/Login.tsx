import { useState } from 'react';
import { Alert, Button, Col, Container, Form, Row } from 'react-bootstrap';
import { Registration } from './Registration';
import './style.css';

function Login(props: any) {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")

    const handleSubmit = (event: any) => {
        event.preventDefault();
        props.setMessage('');

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
            props.login(email, password);
        }
        else {
            props.setMessage(msg);
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
                        {props.message ? <Alert className="error" variant='danger' onClose={() => props.setMessage('')} dismissible>{props.message}</Alert> : false}
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
                          register={props.register}
                        />
                    </Row>
                </Col>
            </Row>

        </Container>
    )
}

export { Login }
