import { useMemo, useState } from 'react';
import { Alert, Button, Col, Container, Dropdown, DropdownButton, Form, Row } from 'react-bootstrap';
import './style.css';
import { Role } from '../../../models/user';
import { useAuth } from "./AuthContext";

function Registration(props: any) {

    const [email, setEmail] = useState("")
    const [firstname, setFirstname] = useState("")
    const [lastname, setLastname] = useState("")
    const [password, setPassword] = useState("")
    const [repeatPassword, setRepeatPassword] = useState("")
    const [role, setRole] = useState(Role.DataSubject)
    const auth = useAuth();

    const handleRegistration = async (event: any) => {
        event.preventDefault()

        let valid = true;
        let message = ""

        
        if (!email || email === '') {
            valid = false
            message += "Please insert a valid username\r\n"
        }
        if (!firstname || firstname === '') {
            valid = false
            message += "Please insert a valid name\r\n"
        }
        if (!lastname || lastname === '') {
            valid = false
            message += "Please insert a valid surname\r\n"
        }
        if (!password || password === '') {
            valid = false
            message += "Please insert a valid password\r\n"
        }
        if (role !== Role.DataSubject && password !== repeatPassword) {
            valid = false
            message += "Passwords do not match\r\n"
        }
        if (valid) {
            try {
                await auth.register(email, firstname, lastname, password, role)
                props.setRegistrationMessage("registrazione avvenuta con successo")
	            }
	            catch(err) {
	                const msg = err instanceof Error ? err.message : String(err);
	                props.setRegistrationMessage(msg)
	                console.log(err)
	            }

            
        } else {
            console.log(message)
            props.setRegistrationMessage(message)
        }
    }

    const roleLabel = useMemo(() => {
        if (role === Role.DatController) return "Data Controller";
        if (role === Role.DPO) return "DPO";
        return "Data Subject";
    }, [role]);

    return (
        <Container fluid>
            <h2>Registration</h2>
            {props.registrationMessage ? <Alert className="error" variant='danger' onClose={() => props.setRegistrationMessage('')} dismissible>{props.registrationMessage}</Alert> : false}
            <Form.Group className="form" controlId='registration'>
                <div className="mt-3 d-flex align-items-center" style={{ gap: '8px' }}>
                    <span>Tipo account:</span>
                    <DropdownButton size="sm" variant="secondary" id="role-dropdown" title={roleLabel} onSelect={(key) => key && setRole(key as Role)}>
                        <Dropdown.Item eventKey={Role.DataSubject}>Data Subject</Dropdown.Item>
                        <Dropdown.Item eventKey={Role.DatController}>Data Controller</Dropdown.Item>
                        <Dropdown.Item eventKey={Role.DPO}>DPO</Dropdown.Item>
                    </DropdownButton>
                </div>
                { role == Role.DataSubject ?
                <>
                <Form.Control className="mt-3" placeholder="Name" value={firstname} onChange={ev => setFirstname(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Surname" value={lastname} onChange={ev => setLastname(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Smartotum Email" value={email} onChange={ev => setEmail(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Smartotum Password" type='password' value={password} onChange={ev => setPassword(ev.target.value)} />
                <Button variant='warning' type='submit' className='loginBtn' onClick={handleRegistration}>Register with Smartotum</Button>
                </>
                :
                <>
                <Form.Control className="mt-3" placeholder="Email" value={email} onChange={ev => setEmail(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Name" value={firstname} onChange={ev => setFirstname(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Surname" value={lastname} onChange={ev => setLastname(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Password" type='password' value={password} onChange={ev => setPassword(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Confirm Password" type='password' value={repeatPassword} onChange={ev => setRepeatPassword(ev.target.value)} />
                <Button variant='warning' type='submit' className='loginBtn' onClick={handleRegistration}>Create new Account</Button>
                </>           
                }
                   </Form.Group>
            <hr></hr>

        </Container>
    )
}

export { Registration }
