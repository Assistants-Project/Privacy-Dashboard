class ConsentModel {
  uuid: string;
  content: string;
  given?: boolean;
  given_at?: string;

  constructor(uuid: string, content: string, given?: boolean, given_at?: string) {
    this.uuid = uuid;
    this.content = content;
    this.given = given;
    this.given_at = given_at;
  }
}

export { ConsentModel };
