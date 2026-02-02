import { getDpos } from "../API/User/userAPI";
import { Role, User } from "../models/user";

type UserDto = {
  uuid: string;
  email: string;
  firstname: string;
  lastname: string;
  role: Role;
};

const toUserModel = (dto: UserDto): User =>
  new User(dto.uuid, dto.email, dto.firstname, dto.lastname, dto.role);

export const fetchDataProtectionOfficers = async (): Promise<User[] | undefined> => {
  const payload = (await getDpos()) as unknown;
  if (!Array.isArray(payload)) {
    console.warn("Unexpected dpos payload:", payload);
    return undefined;
  }

  return (payload as UserDto[]).map(toUserModel);
};

