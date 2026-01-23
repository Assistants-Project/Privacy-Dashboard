import { useMemo, useState } from 'react';
import { Alert, Button, Col, Container, Dropdown, DropdownButton, Form, Row } from 'react-bootstrap';
import './style.css';

function Registration(props: any) {

    const [newEmail, setNewEmail] = useState("")
    const [name, setName] = useState("")
    const [surname, setSurname] = useState("")
    const [newPassword, setNewPassword] = useState("")
    const [repeatPassword, setRepeatPassword] = useState("")
    const [role, setRole] = useState("DataSubject")

    const handleRegistration = (event: any) => {
        event.preventDefault()
        props.setMessage("")

        let valid = true;
        let message = ""

        props.register(newEmail, name, surname, newPassword, role)

        
        if (!newEmail || newEmail === '') {
            valid = false
            message += "Please insert a valid username\r\n"
        }
        if (!name || name === '') {
            valid = false
            message += "Please insert a valid name\r\n"
        }
        if (!surname || surname === '') {
            valid = false
            message += "Please insert a valid surname\r\n"
        }
        if (!newPassword || newPassword === '') {
            valid = false
            message += "Please insert a valid password\r\n"
        }
        if (newPassword !== repeatPassword) {
            valid = false
            message += "Passwords do not match\r\n"
        }
        if (valid) {
            props.register(newEmail, name, surname, newPassword, role)
        } else {
            console.log(message)
            props.setRegistrationMessage(message)
        }
    }

    const roleLabel = useMemo(() => {
        if (role === "DataController") return "Data Controller";
        if (role === "DPO") return "DPO";
        return "Data Subject";
    }, [role]);

    return (
        <Container fluid>
            <h2>Registration</h2>
            {props.registrationMessage ? <Alert className="error" variant='danger' onClose={() => props.setRegistrationMessage('')} dismissible>{props.registrationMessage}</Alert> : false}
            <Form.Group className="form" controlId='registration'>
                <div className="mt-3 d-flex align-items-center" style={{ gap: '8px' }}>
                    <span>Tipo account:</span>
                    <DropdownButton size="sm" variant="secondary" id="role-dropdown" title={roleLabel} onSelect={(key) => key && setRole(key)}>
                        <Dropdown.Item eventKey="DataSubject">Data Subject</Dropdown.Item>
                        <Dropdown.Item eventKey="DataController">Data Controller</Dropdown.Item>
                        <Dropdown.Item eventKey="DPO">DPO</Dropdown.Item>
                    </DropdownButton>
                </div>
                { role == "DataSubject" ?
                <>
                <Form.Control className="mt-3" placeholder="Name" value={name} onChange={ev => setName(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Surname" value={surname} onChange={ev => setSurname(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Smartotum Email" value={newEmail} onChange={ev => setNewEmail(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Smartotum Password" type='password' value={newPassword} onChange={ev => setNewPassword(ev.target.value)} />
                <Button variant='warning' type='submit' className='loginBtn' onClick={handleRegistration}>Register with Smartotum</Button>
                </>
                :
                <>
                <Form.Control className="mt-3" placeholder="Email" value={newEmail} onChange={ev => setNewEmail(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Name" value={name} onChange={ev => setName(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Surname" value={surname} onChange={ev => setSurname(ev.target.value)} />
                <Form.Control className="mt-3" placeholder="Password" type='password' value={newPassword} onChange={ev => setNewPassword(ev.target.value)} />
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
