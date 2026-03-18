import { io } from "socket.io-client";

let socketInstance = null;

const getSocketBaseUrl = () => {
  const rawApiUrl = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000";
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
    transports: ["websocket", "polling"],
    reconnection: true,
    reconnectionAttempts: 10,
    reconnectionDelay: 1000,
  });

  return socketInstance;
};
