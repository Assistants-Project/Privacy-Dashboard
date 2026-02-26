import { Button, Card, Col, Row } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { User } from "../../models/user";
import { useHome } from "../../contexts/HomeContext";

export function UserMenu() {
    const { user, logout, deleteUser, isDataSubject } = useAuth();
    const { current_home_uuid } = useHome();


    return (
        <>
            <Card style={{ minWidth: 350 }} className="border-0 shadow-none">
                <Card.Title className="text-center"> {user?.firstname + " " + user?.lastname}
                </Card.Title>

                <Card.Subtitle className="text-center mb-3 text-muted">

                </Card.Subtitle>

                <Card.Text as="div">
                    <Row className="align-items-start mb-2">
                        <Col>
                            Email
                        </Col>
                        <Col className="text-end">
                            {user?.email}
                        </Col>
                    </Row>
                    <Row className="align-items-start mb-2">
                        <Col xs="auto">Role</Col>
                        <Col className="text-end">{user?.role}</Col>
                    </Row>

                    {isDataSubject && 
                    
                    <Row className="align-items-start mb-2">
                        <Col xs="auto">Selected Home</Col>
                        <Col className="text-end">{current_home_uuid}</Col>
                    </Row>

                    }
                    
                    <Row className="justify-content-center">
                        <Col xs="auto">
                        <Button variant="outline-warning" onClick={logout}>
                            Exit
                        </Button>
                        </Col>
                        <Col xs="auto">
                        <Button variant="danger" onClick={deleteUser}>
                            DELETE USER
                        </Button>
                        </Col>
                    </Row>

                </Card.Text>
                
            </Card>

        </>

    )



}
