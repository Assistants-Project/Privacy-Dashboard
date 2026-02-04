import { useEffect } from "react";
import { Button, Col, Container, Row } from "react-bootstrap";
import { useAuth } from "./Authentication/AuthContext";
import { useNavigate } from "react-router-dom";
import { HomeModel } from "../models/home";
import { Role, User } from "../models/user";
import { HomeSelector } from "./HomeSelector";

function Home() {
  const auth = useAuth();
  const isDataSubject = auth.user?.role === Role.DataSubject;

  return (
    <Container className="py-3">
      <Row className="mb-3">
        <Col>
          <h2>Benvenuto</h2>
          <h3> {auth.user ? `${auth.user.firstname} ${auth.user.lastname}` : ""}</h3>
        </Col>
      </Row>
      <Row>
        <Col>
          {isDataSubject && <HomeSelector />}
        </Col>
      </Row>
    </Container>

  );
}

export { Home };
