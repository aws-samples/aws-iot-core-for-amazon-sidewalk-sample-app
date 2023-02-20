import { ACCESS_TOKEN, UNAUTHORIZE } from "./constants";

export const verifyAuth = (statusCode: number) => {
  if (statusCode === 401) {
    localStorage.removeItem(ACCESS_TOKEN);
    localStorage.setItem(UNAUTHORIZE, "true");
    window.location.reload();
  }
};
