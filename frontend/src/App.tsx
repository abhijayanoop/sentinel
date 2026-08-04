import { useState } from "react";
import { getToken, clearToken } from "./api/client";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(() => getToken() !== null);

  const handleLogout = () => {
    clearToken();
    setLoggedIn(false);
  };

  if (!loggedIn) {
    return <LoginPage onLoggedIn={() => setLoggedIn(true)} />;
  }

  return <DashboardPage onLogout={handleLogout} />;
}
