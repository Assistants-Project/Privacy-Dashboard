import { Button, Card, Col, Container, Row } from "react-bootstrap";
import { useAuth } from "./Authentication/AuthContext";
import { HomeModel } from "../models/home";
import { Role, User } from "../models/user";
import { useHome } from "./HomeContext";

function HomeSelector() {
    const auth = useAuth();
    const {current_home_uuid,homes,updateCurrentHomeUUID} = useHome();

    const renderOptional = (value: string | undefined) =>
        value && value.trim() ? value : <span className="muted">Non impostato</span>;

    return (
        <>
        <Container className="mt-3">
            <Row>
                <Col>
                    <h2>Home selection</h2>
                    <p className="muted">Click on a home to select as a current home</p>
                </Col>
            </Row>
            <Row>
                {homes?.length ? (
                    <Col className="d-flex flex-nowrap gap-3 overflow-auto pb-2">
                        {homes.map((home, idx) => {
                            const isSelected = current_home_uuid === home.uuid 
                            return (
                                <Card
                                    key={home.uuid || idx}
                                    className={`${isSelected ? "border-3 border-primary" : ""}`}
                                    id="house_card"
                                    style={{ minWidth: 280 }}
                                    onClick={() => current_home_uuid !== home.uuid && updateCurrentHomeUUID(home.uuid)}
                                >
                                    <Card.Title className="text-center"> {home.name?.trim()
                                        ? home.name
                                        : "Nome non impostato"}
                                    </Card.Title>

                                    <Card.Subtitle className="text-center mb-3 text-muted">
                                        UUID:{" "}
                                        {home.uuid?.trim() ? home.uuid : "Non impostato"}
                                    </Card.Subtitle>

                                    <Card.Text as="div">
                                        <Row className="align-items-start">
                                            <Col xs="auto">
                                                Address
                                            </Col>
                                            <Col className="text-end">
                                                {renderOptional(home.address)}
                                            </Col>
                                        </Row>
                                        <Row className="align-items-start">
                                            <Col xs="auto">ZIP</Col>
                                            <Col className="text-end">{renderOptional(home.zip_code)}</Col>
                                        </Row>
                                        <Row className="align-items-start">
                                            <Col xs="auto">Country</Col>
                                            <Col className="text-end">{renderOptional(home.country)}</Col>
                                        </Row>

                                    </Card.Text>
                                </Card>
                            );
                        })}
                    </Col>
                ) : (
                    <Col className="card">
                        <div>Nessuna casa disponibile.</div>
                        <div className="muted">
                            La lista potrebbe essere vuota oppure non caricata.
                        </div>
                    </Col>
                )}
            </Row>
            </Container>
        </>
    );
}

export { HomeSelector };
