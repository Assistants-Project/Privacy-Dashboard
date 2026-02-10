import { useMemo, useState } from 'react';
import { Alert, Button, Card, Col, Container, Dropdown, DropdownButton, Form, Row } from 'react-bootstrap';
import { Role } from '../../models/user';
import { useAuth } from "../../contexts/AuthContext";

function Registration() {

    const [email, setEmail] = useState("")
    const [firstname, setFirstname] = useState("")
    const [lastname, setLastname] = useState("")
    const [password, setPassword] = useState("")
    const [repeatPassword, setRepeatPassword] = useState("")
    const [role, setRole] = useState(Role.DataSubject)

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const auth = useAuth();

    const roleLabel = useMemo(() => {
        if (role === Role.DataController) return "Data Controller";
        if (role === Role.DPO) return "Data Protection Officer";
        return "Data Subject";
    }, [role]);


    const handleRegistration = async (event: any) => {

        setSuccess("")
        event.preventDefault()
        setError("");

        let valid = true;
        let message = ""


        if (email.trim() === "") {
            valid = false
            message += "Please insert a valid email\n"
        }
        if (firstname.trim() === "") {
            valid = false
            message += "Please insert a valid name\n"
        }
        if (lastname.trim() === "") {
            valid = false
            message += "Please insert a valid surname\n"
        }
        if (password === "") {
            valid = false
            message += "Please insert a valid password\n"
        }
        if (role !== Role.DataSubject && password !== repeatPassword) {
            valid = false
            message += "Passwords do not match\n"
        }
        if (valid) {
            try {
                await auth.register(email.trim(), firstname.trim(), lastname.trim(), password, role)
                setSuccess("Registration Successful\nPlease Log In!");
                setEmail("");
                setError("");
                setFirstname("");
                setLastname("");
                setPassword("");
                setRepeatPassword("");
                setRole(Role.DataSubject);
            }
            catch (err) {
                setError(err instanceof Error ? err.message : String(err));
            }

        } else {
            setError(message);
        }
    }
    return (

        <Card>
            <Card.Body>
                <Card.Title>Registration</Card.Title>
                <Row className="justify-content-center mt-4">
                    <Col xs="auto">
                        <Form onSubmit={handleRegistration} className="d-flex flex-column gap-4">
                            <Form.Group>
                                <Row className="align-items-center">
                                    <Col xs="auto" className="pe-0">
                                        Account Type:
                                    </Col>
                                    <Col xs="auto" className="pe-0">
                                        <DropdownButton style={{ minWidth: 170 }} size="sm" variant="secondary" title={roleLabel} onSelect={(key) => key && setRole(key as Role)}>
                                            <Dropdown.Item eventKey={Role.DataSubject}>Data Subject</Dropdown.Item>
                                            <Dropdown.Item eventKey={Role.DataController}>Data Controller</Dropdown.Item>
                                            <Dropdown.Item eventKey={Role.DPO}>Data Protection Officer</Dropdown.Item>
                                        </DropdownButton>
                                    </Col>
                                </Row>
                                {role == Role.DataSubject ?
                                    <>
                                        <Form.Control className="mt-3" placeholder="Name" value={firstname} onChange={ev => setFirstname(ev.target.value)} />
                                        <Form.Control className="mt-3" placeholder="Surname" value={lastname} onChange={ev => setLastname(ev.target.value)} />
                                        <Form.Control className="mt-3" placeholder="Smartotum Email" value={email} onChange={ev => setEmail(ev.target.value)} />
                                        <Form.Control className="mt-3" placeholder="Smartotum Password" type='password' value={password} onChange={ev => setPassword(ev.target.value)} />
                                    </>
                                    :
                                    <>
                                        <Form.Control className="mt-3" placeholder="Email" value={email} onChange={ev => setEmail(ev.target.value)} />
                                        <Form.Control className="mt-3" placeholder="Name" value={firstname} onChange={ev => setFirstname(ev.target.value)} />
                                        <Form.Control className="mt-3" placeholder="Surname" value={lastname} onChange={ev => setLastname(ev.target.value)} />
                                        <Form.Control className="mt-3" placeholder="Password" type='password' value={password} onChange={ev => setPassword(ev.target.value)} />
                                        <Form.Control className="mt-3" placeholder="Confirm Password" type='password' value={repeatPassword} onChange={ev => setRepeatPassword(ev.target.value)} />
                                    </>
                                }

                            </Form.Group>
                            <Button variant="secondary" className="align-self-center w-auto" type="submit">{role == Role.DataSubject ? "Register with Smartotum" : "Create new Account"}</Button>
                        </Form>
                    </Col>
                </Row>
            </Card.Body>
            {error ? <Alert variant='danger' onClose={() => setError("")} style={{ whiteSpace: "pre-line" }} dismissible>{error}</Alert> : undefined}
            {success ? <Alert variant='success' onClose={() => setSuccess("")} style={{ whiteSpace: "pre-line" }} dismissible>{success}</Alert> : undefined}
        </Card>

    )
}

export { Registration }
