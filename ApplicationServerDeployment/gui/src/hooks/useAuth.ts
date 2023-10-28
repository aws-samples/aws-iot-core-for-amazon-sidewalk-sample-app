import { useEffect, useState } from "react";
import { apiClient, setAuthHeader, setUsernameHeader } from "../apiClient";
import { ENDPOINTS } from "../endpoints";
import { logger } from "../utils/logger";
import toast from "react-hot-toast";
import { ACCESS_TOKEN, UNAUTHORIZE } from "../constants";
import { useNavigate, useRoutes } from "react-router";
import { Routes } from "../routes";

export const useAuth = () => {
  const [isLogginIn, setIsLogginIn] = useState(false);
  const [isAuthorized, setIsAuthorized] = useState(() => !!localStorage.getItem(ACCESS_TOKEN));
  const navigate = useNavigate();

  const login = async (username: string, password: string) => {
    setIsLogginIn(true);
    try {
      setUsernameHeader(username);
      const response = await apiClient.post<string>(ENDPOINTS.login, {
        username,
        password,
      });
      setAuthHeader(response.data);
      setIsAuthorized(true);
      navigate(Routes.sensorMonitoring);
    } catch (error) {
      logger.log("error during login", error);
      toast.error("User or password incorrect");
    } finally {
      setIsLogginIn(false);
    }
  };

  // check for auth error var to show a message in case user gets logged out
  useEffect(() => {
    if (localStorage.getItem(UNAUTHORIZE)) {
      setTimeout(() => {
        toast.error("Unauthorize error");
        localStorage.removeItem(UNAUTHORIZE);
      }, 0);
    }
  }, []);

  return { login, isLogginIn, isAuthorized };
};
