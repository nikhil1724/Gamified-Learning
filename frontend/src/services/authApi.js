import api, { publicApi } from "./api";

const FALLBACK_STATUSES = new Set([404, 405]);

const postWithFallback = async (paths, payload) => {
  let lastError;
  for (let index = 0; index < paths.length; index += 1) {
    const path = paths[index];
    try {
      return await publicApi.post(path, payload);
    } catch (error) {
      lastError = error;
      const status = error?.response?.status;
      const shouldTryNext = FALLBACK_STATUSES.has(status) && index < paths.length - 1;
      if (!shouldTryNext) {
        throw error;
      }
    }
  }
  throw lastError;
};

export const registerUser = (payload) => publicApi.post("/auth/register", payload);

export const verifyRegistrationOtp = (payload) =>
  postWithFallback(["/auth/verify-otp", "/verify-otp", "/verify-registration-otp"], payload);

export const resendRegistrationOtp = (payload) =>
  postWithFallback(["/auth/resend-otp", "/resend-otp"], payload);

export const loginUser = (payload) =>
  postWithFallback(["/auth/login", "/login"], payload);

export default {
  registerUser,
  verifyRegistrationOtp,
  resendRegistrationOtp,
  loginUser,
  authenticated: api,
};
