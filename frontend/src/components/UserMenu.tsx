import { Button, Card, Col, Container, Row } from "react-bootstrap";
import { useAuth } from "./Authentication/AuthContext";
import { HomeModel } from "../models/home";
import { Role, User } from "../models/user";

export function UserMenu() {
    const { user, logout, delete_user } = useAuth();




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

                    {user?.role == Role.DataSubject && 
                    
                    <Row className="align-items-start mb-2">
                        <Col xs="auto">Selected Home</Col>
                        <Col className="text-end">{user?.current_home?.uuid}</Col>
                    </Row>

                    }
                    
                    <Row className="justify-content-center">
                        <Col xs="auto">
                        <Button variant="outline-warning" onClick={logout}>
                            Exit
                        </Button>
                        </Col>
                        <Col xs="auto">
                        <Button variant="danger" onClick={delete_user}>
                            DELETE USER
                        </Button>
                        </Col>
                    </Row>

                </Card.Text>
                
            </Card>

        </>

    )



}