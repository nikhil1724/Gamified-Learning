import api, { publicApi } from "./api";

export const registerUser = (payload) => publicApi.post("/register", payload);
export const verifyOtp = (payload) => publicApi.post("/verify-otp", payload);
export const resendOtp = (payload) => publicApi.post("/resend-otp", payload);
export const loginUser = (payload) => publicApi.post("/login", payload);

export default {
  registerUser,
  verifyOtp,
  resendOtp,
  loginUser,
  authenticated: api,
};
