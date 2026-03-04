import "bootstrap/dist/css/bootstrap.min.css";
import "./styles/globals.css";
import "./styles/button.css";
import "./styles/card.css";
import "./styles/badge.css";
import "./styles/form.css";
import "./theme.css";
import React from "react";
import { createRoot } from "react-dom/client";

import App from "./App";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";

const container = document.getElementById("root");
const root = createRoot(container);

root.render(
	<ThemeProvider>
		<AuthProvider>
			<App />
		</AuthProvider>
	</ThemeProvider>
);
