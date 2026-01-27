import { Button, Card, Col, Container, Row } from "react-bootstrap";
import { useAuth } from "../../components/Authentication/AuthContext";
import { HomeModel } from "../../models/home";
import { Role, User } from "../../models/user";
import { fetchInstalledApplications } from "../../services/ApplicationService"
import { useEffect, useState } from "react";
import { AppModel } from "../../models/app";
import CloseButton from 'react-bootstrap/CloseButton';


export function Apps() {
    const { user, logout, delete_user, loading } = useAuth();
    const [apps, setApps] = useState<AppModel[] | undefined>(undefined);
    const [current_app, setCurrentApp] = useState<number | undefined>(undefined);


    //redirect user to the home page if a session is established
    useEffect(() => {

        if (loading) return;

        const homeUuid = user?.current_home?.uuid;
        if (!homeUuid) return;

        (async () => {
            const res = await fetchInstalledApplications(homeUuid);
            setApps(res);
            setCurrentApp(1);
        })();

    }, [loading, user?.current_home?.uuid]);


    return (

        <Container>
            <Row>
                <Col>
                    <h2>Selezione App</h2>
                    <p className="muted">Clicca su un app per vedere i dettagli</p>
                </Col>
            </Row>

            <Row className="align-items-start g-4">
                <Col>

                    <Row xs={2} md={3}>

                        {apps?.length ? (
                            <>
                                {apps.map((app, idx) => {
                                    return (
                                        <Col>
                                            <Card
                                                key={app.uuid}
                                                className="m-2"
                                                id=""

                                                onClick={() => {setCurrentApp(idx)}}
                                            >
                                                <Card.Title className="text-center"> {app.name.trim()
                                                    ? app.name
                                                    : "Nome non impostato"}
                                                </Card.Title>

                                                <Card.Subtitle className="text-center mb-3 text-muted">
                                                    Description:{" "}
                                                    {app.description}
                                                </Card.Subtitle>

                                            </Card>
                                        </Col>
                                    );

                                })}

                            </>
                        ) : (
                            <Col>
                                <div>Nessuna applicazione disponibile.</div>
                                <div className="muted">
                                    La lista potrebbe essere vuota oppure non caricata.
                                </div>
                            </Col>
                        )}

                    </Row>

                </Col>

                <Col className="col-4">
                    {
                        current_app!=undefined && apps?.[current_app] &&
                        <>
                            <Card
                                key={apps?.[current_app].name}
                                className=""
                                id=""
                                style={{ minWidth: 280 }}
                            // onClick={}
                            >
                                <div className="d-flex justify-content-between align-items-start">
                                <Card.Title className="text-center"> {apps?.[current_app].name.trim()
                                    ? apps?.[current_app].name
                                    : "Nome non impostato"}
                                <CloseButton onClick={() => setCurrentApp(undefined)}></CloseButton>
                                </Card.Title>
                                </div>

                                <Card.Subtitle className="text-center mb-3 text-muted">
                                    Description:{" "}
                                    {apps?.[current_app].description}
                                </Card.Subtitle>

                                <Card.Text as="div">
                                    <Row className="align-items-start">
                                        <Col xs="auto">
                                            Description
                                        </Col>
                                        <Col className="text-end">
                                            {apps?.[current_app].description}
                                        </Col>
                                    </Row>
                                    <Row className="align-items-start">
                                        <Col xs="auto">installed at</Col>
                                        <Col className="text-end">{apps?.[current_app].installed_at}</Col>
                                    </Row>
                                    {/* <Row className="align-items-start">
                                            <Col xs="auto">Country</Col>
                                            <Col className="text-end">{renderOptional(home.country)}</Col>
                                        </Row> */}

                                </Card.Text>
                            </Card>
                        </>
                    }

                </Col>








            </Row>




        </Container>
    )

}