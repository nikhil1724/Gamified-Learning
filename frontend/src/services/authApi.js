import api, { publicApi } from "./api";

export const registerUser = (payload) => publicApi.post("/register", payload);
export const loginUser = (payload) => publicApi.post("/login", payload);

export default {
  registerUser,
  loginUser,
  authenticated: api,
};
