import { io } from "socket.io-client";
import { resolveBaseApiUrl } from "./api";

let socketInstance = null;

const getSocketBaseUrl = () => {
  const rawApiUrl = resolveBaseApiUrl();
  const normalizedApiUrl = rawApiUrl.replace(/\/+$/, "");

  if (normalizedApiUrl.endsWith("/api")) {
    return normalizedApiUrl.replace(/\/api$/, "");
  }

  return normalizedApiUrl;
};

export const getLeaderboardSocket = () => {
  if (socketInstance) {
    return socketInstance;
  }

  socketInstance = io(getSocketBaseUrl(), {
    transports: ["polling"],
    upgrade: false,
    reconnection: true,
    reconnectionAttempts: 10,
    reconnectionDelay: 1000,
  });

  return socketInstance;
};
