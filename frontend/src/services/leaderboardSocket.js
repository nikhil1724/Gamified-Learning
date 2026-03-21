import { io } from "socket.io-client";
import { BASE_URL } from "./api";

let socketInstance = null;
const ENABLE_REALTIME = process.env.REACT_APP_ENABLE_REALTIME === "true";

const createNoopSocket = () => ({
  connected: false,
  on: () => {},
  off: () => {},
  emit: () => {},
  disconnect: () => {},
});

const getSocketBaseUrl = () => {
  const normalizedApiUrl = BASE_URL.replace(/\/+$/, "");

  if (normalizedApiUrl.endsWith("/api")) {
    return normalizedApiUrl.replace(/\/api$/, "");
  }

  return normalizedApiUrl;
};

export const getLeaderboardSocket = () => {
  if (socketInstance) {
    return socketInstance;
  }

  // Realtime is optional. Keep HTTP polling as the default for sync-worker deployments.
  if (!ENABLE_REALTIME) {
    socketInstance = createNoopSocket();
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
