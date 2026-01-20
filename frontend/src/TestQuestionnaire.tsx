import {
  Button,
  Form,
  FormSelect,
  OverlayTrigger,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
} from "react-bootstrap";
import { useState, useEffect, useRef } from "react";
import {
  getQuestionnaireByManagedApplicationUuid,
  getQuestionnaireQuestions,
  submitQuestionnaireByManagedApplicationUuid,
} from "../API/questionAPI";
import { Question, Evaluation } from "../models/question";

function TestQuestionnaire(props: any) {
  const [questions, setQuestions] = useState<Question[] | null>(null);
  const [applicationEvaluation, setApplicationEvaluation] =
    useState<Evaluation | null>(null);
  const answersRef = useRef<Record<string, string>>({}); // will have key value pairs of questionUuid -> givenAnswer

  // TODO: move this application fetching logic elsewhere and pass data here via props if needed
  const [managedApplications, setManagedApplications] = useState<any[]>([]);
  const [selectedApplicationUuid, setSelectedApplicationUuid] =
    useState<string>("");

  useEffect(() => {
    const fetchData = async () => {
      const applications = await props.fetchManagedApplications();
      setManagedApplications(applications || []);
    };
    fetchData();
  }, []);

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
    }
    setSelectedApplicationUuid(applicationUuid);
    setApplicationEvaluation(null); // reset any previous evaluation shown
  };

  const saveGivenAnswer = (questionUuid: string, answer: string) => {
    answersRef.current[questionUuid] = answer; // write to ref only to avoid rerendering the whole component on each answer change
  };

  const handleSubmitAnswers = async () => {
    let submissionPayload = {
      check_required: true,
      answers: Object.entries(answersRef.current).map(([key, value]) => ({
        question_uuid: key,
        answer_content: value,
      })),
    };
    const submittedQuestionnaire = await submitQuestionnaire(
      selectedApplicationUuid,
      submissionPayload,
    );
    // TODO: for simplicity, we fetch directly here the submitted questionnaire to verify it was stored correctly, REMOVE THIS!
    const fetchedQuestionnaireResult =
      await handleGetQuestionnaireByApplication(selectedApplicationUuid);
    console.log("Submitted :", submittedQuestionnaire.application_evaluation);
    console.log(
      "Fetched Questionnaire:",
      fetchedQuestionnaireResult.application_evaluation,
    );
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
      setSelectedApplicationUuid(""); // reset application selection
    } else {
      alert("Error verifying the submitted Questionnaire.");
    }
  };

  const handleGetQuestionnaireByApplication = async (
    applicationUuid: string,
  ) => {
    try {
      const result =
        await getQuestionnaireByManagedApplicationUuid(applicationUuid);
      console.log("Questionnaire retrieved successfully");
      return result;
    } catch (err) {
      console.error("Error getting questionnaire:", err);
    }
  };

  const fetchQuestionnaire = async (): Promise<Question[] | undefined> => {
    try {
      const result = await getQuestionnaireQuestions();
      console.log("Questionnaire template retrieved successfully");
      return result.map(
        (q: any) =>
          ({
            uuid: q.question.uuid,
            content: q.question.content,
            additionalInformation: q.question.additional_information,
            choices: q.choices,
          }) as Question,
      );
    } catch (err) {
      console.error("Error getting questionnaire template:", err);
    }
  };

  const submitQuestionnaire = async (
    applicationUuid: string,
    piaTemplate: any,
  ) => {
    try {
      const result = await submitQuestionnaireByManagedApplicationUuid(
        applicationUuid,
        piaTemplate,
      );
      console.log("Privacy Impact Assessment submitted successfully");
      return result;
    } catch (err) {
      console.error("Error submitting privacy impact assessment:", err);
      alert(`Error submitting privacy impact assessment: ${err}`);
    }
  };

  return (
    <div className="d-flex flex-column align-items-center p-4">
      <h1>Questionnaire</h1>
      <div className="w-50">
        <p>Choose a managed application to submit a questionnaire for:</p>
        <FormSelect
          className="mb-3"
          onChange={(e) => setChosenApplication(e.target.value)}
          value={selectedApplicationUuid}
        >
          <option className="d-none" value="" disabled>
            Select an application
          </option>
          {managedApplications.map((app) => (
            <option key={app.application.uuid} value={app.application.uuid}>
              {app.application.name}
            </option>
          ))}
        </FormSelect>
      </div>
      {selectedApplicationUuid && (
        <div className="w-75 border border-black rounded shadow-sm p-3">
          {questions?.map((question, idx) => (
            <div
              key={`${question.uuid}-${selectedApplicationUuid || "none"}`}
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
                  <div key={`inline-${question.uuid}`} className="my-2">
                    {question.choices?.map((choice, idx) => (
                      <Form.Check
                        inline
                        label={choice}
                        value={choice}
                        name={`group-${question.uuid}`}
                        type="radio"
                        id={`inline-${question.uuid}-${idx}-${selectedApplicationUuid || "none"}`}
                        key={`inline-${question.uuid}-${idx}-${selectedApplicationUuid || "none"}`}
                        defaultChecked={
                          answersRef.current[question.uuid] === choice
                        }
                        onChange={(e) =>
                          saveGivenAnswer(question.uuid, e.target.value)
                        }
                      />
                    ))}
                  </div>
                </Form>
              )}
            </div>
          ))}
          <Button variant="dark" onClick={handleSubmitAnswers} className="mt-3">
            Submit Answers
          </Button>
        </div>
      )}
      {!selectedApplicationUuid && applicationEvaluation && (
        <div className="w-75 border border-black rounded shadow-sm p-3">
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
                <strong>Answer:</strong> {question.answerContent}
              </p>
              {question.evaluation && (
                <p className="mt-2">
                  <strong>Evaluation:</strong>{" "}
                  <span
                    style={{
                      color: question.evaluation.toLowerCase(),
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
      <Button variant="secondary" onClick={props.onLogout} className="mt-3">
        Logout
      </Button>
    </div>
  );
}

export { TestQuestionnaire };
