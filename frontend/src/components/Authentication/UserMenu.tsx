import { useState } from "react";
import { Button, Card, Col, Row } from "react-bootstrap";
import { useAuth } from "../../contexts/AuthContext";
import { useHome } from "../../contexts/HomeContext";
import { UpdateProfileModal } from "./UpdateProfileModal";

export function UserMenu() {
    const { user, logout, deleteUser, isDataSubject } = useAuth();
    const { current_home_uuid } = useHome();
    const [showUpdateProfile, setShowUpdateProfile] = useState(false);

    return (
        <>
            <Card style={{ minWidth: 350 }} className="border-0 shadow-none">
                <Card.Title className="text-center"> {user?.firstname + " " + user?.lastname}
                </Card.Title>

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
                    
                    <div className="d-flex flex-wrap justify-content-center gap-2 mt-3">
                        {!isDataSubject &&
                        <Button variant="outline-primary" onClick={() => setShowUpdateProfile(true)}>
                            UPDATE PROFILE
                        </Button>
                        }
                        <Button variant="danger" onClick={deleteUser}>
                            DELETE PROFILE
                        </Button>
                    </div>
                    <div className="d-flex justify-content-center mt-2">
                        <Button variant="outline-warning" onClick={logout}>
                            Logout
                        </Button>
                    </div>

                </Card.Text>
                
            </Card>
            {!isDataSubject && <UpdateProfileModal show={showUpdateProfile} onHide={() => setShowUpdateProfile(false)} />}
        </>

    )



}
