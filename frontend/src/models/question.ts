export interface Question {
  uuid: string;
  content: string;
  additionalInformation?: string;
  choices?: string[];
  answerContent?: string;
  evaluation?: Evaluation;
}

export enum Evaluation {
  GREEN = "GREEN",
  ORANGE = "ORANGE",
  RED = "RED",
}

export class Questionnaire {
  application_uuid: string;
  questions: Question[];
  application_evaluation?: Evaluation;
  questionnaire_summary?: string;

  constructor(
    application_uuid: string,
    questions: Question[],
    application_evaluation?: Evaluation,
    questionnaire_summary?: string,
  ) {
    this.application_uuid = application_uuid;
    this.questions = questions;
    this.application_evaluation = application_evaluation;
    this.questionnaire_summary = questionnaire_summary;
  }
}
