import api, { publicApi } from "./api";

const postAuth = async (path, payload) => {
  try {
    return await publicApi.post(path, payload);
  } catch (error) {
    console.error(`Auth API ${path} failed:`, error);
    throw error;
  }
};

export const registerUser = (payload) => postAuth("/register", payload);

export const verifyRegistrationOtp = (payload) => postAuth("/auth/verify-otp", payload);

export const resendRegistrationOtp = (payload) => postAuth("/auth/resend-otp", payload);

export const loginUser = (payload) => postAuth("/login", payload);

export const googleLoginUser = (payload) => postAuth("/auth/google-login", payload);

export default {
  registerUser,
  verifyRegistrationOtp,
  resendRegistrationOtp,
  loginUser,
  googleLoginUser,
  authenticated: api,
};
