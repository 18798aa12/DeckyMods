/** Only redacted RPC messages and fixed application messages use this type. */
export class UserFacingError extends Error {
  readonly name = "UserFacingError";
}
