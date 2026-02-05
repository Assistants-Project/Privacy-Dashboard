import {
  Button,
  Card,
  Col,
  Container,
  Form,
  OverlayTrigger,
  Row,
  Tooltip,
} from "react-bootstrap";
import { useState, useRef, useCallback, useEffect } from "react";
import { Question, Evaluation } from "../../models/question";
import { useApp } from "../AppsContext";
import {
  fetchQuestionnaire,
  handleGetQuestionnaireByApplication,
  submitQuestionnaire,
} from "../../services/QuestionnaireService";
import { useAuth } from "../Authentication/AuthContext";
import { Role } from "../../models/user";
import { AppsList } from "../AppsList";
import { DocumentStatus } from "../../models/app";

enum QuestionnaireMode {
  ADD = "ADD",
  VIEW = "VIEW",
  EDIT = "EDIT",
}

function Questionnaire(props: any) {
  const [questions, setQuestions] = useState<Question[] | null>(null);
  const [applicationEvaluation, setApplicationEvaluation] =
    useState<Evaluation | null>(null);
  const answersRef = useRef<Record<string, string>>({}); // will have key value pairs of questionUuid -> givenAnswer
  const [mode, setMode] = useState<QuestionnaireMode | null>(null);
  const { user } = useAuth();

  const {
    loadingApps,
    setSelectedAppUUID,
    selectedAppUUID,
    selectedApp,
    managedApps,
    loadQuestionnaire,
  } = useApp();
  const [panelExpanded, setPanelExpanded] = useState(true);


  useEffect(() => {
    if (!selectedAppUUID) return;
    void loadQuestionnaire(selectedAppUUID,false);
  },[loadQuestionnaire,selectedAppUUID,]);



  const closePanel = useCallback(() => {
    setSelectedAppUUID(undefined);
    setMode(null);
  }, [setSelectedAppUUID]);

  useEffect(() => {
    if (loadingApps) return;
    if (!selectedAppUUID) return;
    const isManaged = selectedApp?.pn_status === DocumentStatus.Forbidden;
    if (isManaged) setSelectedAppUUID(undefined);
  }, [loadingApps, managedApps, selectedAppUUID, setSelectedAppUUID]);
  


  // TODO update or remove these functions
  
  const setChosenApplication = async (applicationUuid: string) => {
    const fetchedQuestions = await fetchQuestionnaire();
    setQuestions(fetchedQuestions || []);
    answersRef.current = {};
    const fetchedQuestionnaireResult =
      await handleGetQuestionnaireByApplication(applicationUuid);
    if (fetchedQuestionnaireResult) {
      // seed answersRef from existing questionnaire answers (if present)
      fetchedQuestionnaireResult.given_answers?.forEach((q: any) => {
        answersRef.current[q.question.uuid] = q.answer.answer_content || "";
      });
      setApplicationEvaluation(
        fetchedQuestionnaireResult.application_evaluation,
      );
      setMode(QuestionnaireMode.VIEW);
    } else {
      setApplicationEvaluation(null);
      setMode(QuestionnaireMode.ADD);
    }
    setSelectedAppUUID(applicationUuid);
  };

  const saveGivenAnswer = (questionUuid: string, answer: string) => {
    answersRef.current[questionUuid] = answer; // write to ref only to avoid rerendering the whole component on each answer change
  };

  const handleSubmitAnswers = async () => {
    if (!selectedAppUUID) return;
    let submissionPayload = {
      check_required: true,
      answers: Object.entries(answersRef.current).map(([key, value]) => ({
        question_uuid: key,
        answer_content: value,
      })),
    };
    const submittedQuestionnaire = await submitQuestionnaire(
      selectedAppUUID,
      submissionPayload,
    );
    // TODO: for simplicity, we fetch directly here the submitted questionnaire to verify it was stored correctly, REMOVE THIS!
    const fetchedQuestionnaireResult =
      await handleGetQuestionnaireByApplication(selectedAppUUID);
    if (
      submittedQuestionnaire &&
      fetchedQuestionnaireResult &&
      submittedQuestionnaire.application_evaluation ===
        fetchedQuestionnaireResult.application_evaluation
    ) {
      setQuestions(
        fetchedQuestionnaireResult.given_answers.map(
          (q: any) =>
            ({
              uuid: q.question.uuid,
              content: q.question.content,
              additionalInformation: q.question.additional_information,
              answerContent: q.answer.answer_content,
              evaluation: q.answer.evaluation,
            }) as Question,
        ),
      ); // recreate questions array now with given answers and evaluations
      setApplicationEvaluation(
        fetchedQuestionnaireResult.application_evaluation,
      );
      setMode(QuestionnaireMode.VIEW);
    } else {
      alert("Error verifying the submitted Questionnaire.");
    }
  };

  return (
    <>
      {!loadingApps && managedApps && (
        <Container
          fluid
          className="py-3 d-flex flex-column overflow-hidden h-100"
          style={{ minHeight: 0 }}
        >
          <Row className="mb-3 flex-shrink-0">
            <Col>
              <h1 className="mb-0">Questionnaire</h1>
            </Col>
          </Row>
          <Row
            className="g-3 flex-grow-1 overflow-hidden"
            style={{ minHeight: 0 }}
          >
            <Col
              xs={3}
              lg={4}
              className="d-flex flex-column overflow-hidden"
              style={{ minHeight: 0 }}
            >
              <AppsList
                closePanel={closePanel}
                getDocumentStatus={(app) => app.pn_status}
              />
            </Col>

            <Col
              xs={9}
              lg={8}
              className="d-flex flex-column overflow-hidden"
              style={{ minHeight: 0 }}
            >
              {!selectedApp ? (
                <Card className="p-0">
                  <Card.Body className="text-muted">
                    Select an app to see the Questionnaire.
                  </Card.Body>
                </Card>
              ) : (
                <Card
                  className={
                    panelExpanded
                      ? "p-0 overflow-hidden d-flex flex-column flex-grow-1"
                      : "p-0"
                  }
                  style={panelExpanded ? { minHeight: 0 } : undefined}
                >
                  <Card.Body
                    className={
                      panelExpanded
                        ? "d-flex flex-column flex-grow-1 gap-3 overflow-hidden"
                        : "d-flex flex-column gap-3"
                    }
                    style={panelExpanded ? { minHeight: 0 } : undefined}
                  >
                    <Row
                      className="flex-grow-1 flex-column flex-nowrap overflow-auto m-3 pe-0"
                      style={{ scrollbarWidth: "thin" }}
                    >
                      {(mode === QuestionnaireMode.ADD ||
                        mode === QuestionnaireMode.EDIT) &&
                        selectedAppUUID &&
                        (user?.role === Role.DatController ||
                        user?.role === Role.DPO ? (
                          <div className="w-100 border border-black rounded shadow-sm p-3">
                            {questions?.map((question, idx) => (
                              <div
                                key={`${question.uuid}-${selectedAppUUID || "none"}`}
                                className="w-100 border border-black rounded mb-3 shadow-sm p-3"
                              >
                                <h6>
                                  {idx + 1}. {question.content}&nbsp;
                                  {question.additionalInformation && (
                                    <OverlayTrigger
                                      placement={"top"}
                                      overlay={
                                        <Tooltip id={`tooltip-top`}>
                                          {question.additionalInformation}
                                        </Tooltip>
                                      }
                                    >
                                      <i className="fa-solid fa-circle-info"></i>
                                    </OverlayTrigger>
                                  )}
                                </h6>
                                {(question.choices?.length ?? 0) > 0 && (
                                  <Form>
                                    <div
                                      key={`inline-${question.uuid}`}
                                      className="my-2"
                                    >
                                      {question.choices?.map((choice, idx) => (
                                        <Form.Check
                                          inline
                                          label={choice}
                                          value={choice}
                                          name={`group-${question.uuid}`}
                                          type="radio"
                                          id={`inline-${question.uuid}-${idx}-${selectedAppUUID || "none"}`}
                                          key={`inline-${question.uuid}-${idx}-${selectedAppUUID || "none"}`}
                                          defaultChecked={
                                            answersRef.current[
                                              question.uuid
                                            ] === choice
                                          }
                                          onChange={(e) =>
                                            saveGivenAnswer(
                                              question.uuid,
                                              e.target.value,
                                            )
                                          }
                                        />
                                      ))}
                                    </div>
                                  </Form>
                                )}
                              </div>
                            ))}
                            <Button
                              variant="dark"
                              onClick={handleSubmitAnswers}
                              className="mt-3"
                            >
                              Submit Answers
                            </Button>
                          </div>
                        ) : (
                          <p>No questionnare was found for this application!</p>
                        ))}
                      {mode === QuestionnaireMode.VIEW &&
                        applicationEvaluation && (
                          <div className="w-100 border border-black rounded shadow-sm p-3">
                            <h6 className="mb-3">
                              The submitted questionnaire evaluation is:&nbsp;
                              <span
                                style={{
                                  color: applicationEvaluation.toLowerCase(),
                                  fontWeight: "bold",
                                }}
                              >
                                {applicationEvaluation}
                              </span>
                            </h6>
                            {questions?.map((question, idx) => (
                              <div
                                key={question.uuid}
                                className="w-100 border border-black shadow-sm rounded mb-3 p-3"
                              >
                                <h6>
                                  {idx + 1}. {question.content}&nbsp;
                                  {question.additionalInformation && (
                                    <OverlayTrigger
                                      placement={"top"}
                                      overlay={
                                        <Tooltip id={`tooltip-top`}>
                                          {question.additionalInformation}
                                        </Tooltip>
                                      }
                                    >
                                      <i className="fa-solid fa-circle-info"></i>
                                    </OverlayTrigger>
                                  )}
                                </h6>
                                <p className="mt-2">
                                  <strong>Answer:</strong>{" "}
                                  {question.answerContent}
                                </p>
                                {question.evaluation && (
                                  <p className="mt-2">
                                    <strong>Evaluation:</strong>{" "}
                                    <span
                                      style={{
                                        color:
                                          question.evaluation.toLowerCase(),
                                        fontWeight: "bold",
                                      }}
                                    >
                                      {question.evaluation}
                                    </span>
                                  </p>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                    </Row>
                  </Card.Body>
                </Card>
              )}
            </Col>
          </Row>
        </Container>
      )}
    </>
  );
}

export { Questionnaire };
