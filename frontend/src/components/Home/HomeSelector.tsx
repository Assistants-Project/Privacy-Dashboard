import { Card, Col, Row } from "react-bootstrap";
import { useHome } from "../../contexts/HomeContext";

function HomeSelector() {
    const {current_home_uuid,homes,updateCurrentHomeUUID} = useHome();

    const renderOptional = (value: string | undefined) =>
        value && value.trim() ? value : <span className="muted">Not set</span>;

    return (
        <>
            <Row className="mb-3">
                <Col className="d-flex align-items-baseline gap-2">
                    <h2 className="mb-0">Home selection</h2>
                    <span className="text-muted">| Click on a home to select as a current home</span>
                </Col>
            </Row>
            <Row>
                {homes?.length ? (
                    <Col className="d-flex flex-nowrap gap-3 overflow-auto">
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
                                        : "Name not set"}
                                    </Card.Title>

                                    <Card.Subtitle className="text-center mb-2 text-muted">
                                        UUID:{" "}
                                        {home.uuid?.trim() ? home.uuid : "Not set"}
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
                        <div>No Homes Available</div>
                        <div className="muted">
                            Please refresh the homes with the button on the top right 
                        </div>
                    </Col>
                )}
            </Row>
        </>
    );
}

export { HomeSelector };
