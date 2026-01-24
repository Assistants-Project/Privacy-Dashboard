import { Button, Card, Col, Container, Row } from "react-bootstrap";
import { useAuth } from "./Authentication/AuthContext";
import { HomeModel } from "../../models/home";
import { Role, User } from "../../models/user";

export function UserMenu() {
    const { user, logout } = useAuth();


    return (
        <>
            <Card style={{ minWidth: 350 }}>
                <Card.Title className="text-center"> Alberto Hugonin
                </Card.Title>

                <Card.Subtitle className="text-center mb-3 text-muted">

                </Card.Subtitle>

                <Card.Text>
                    <Row className="align-items-start">
                        <Col xs="auto">
                            Email
                        </Col>
                        <Col className="text-end">
                            {user?.email}
                        </Col>
                    </Row>
                    <Row className="align-items-start">
                        <Col xs="auto">Role</Col>
                        <Col className="text-end">{user?.role}</Col>
                    </Row>
                    <Row className="align-items-start">
                        <Col xs="auto">Current Home</Col>
                        <Col className="text-end">{user?.current_home?.uuid}</Col>
                    </Row>
                    <Row className="align-items-start">
                        <Button variant="warning" className="w-100" onClick={logout}>
                            Logout
                        </Button>
                    </Row>

                </Card.Text>
            </Card>

        </>

    )



}