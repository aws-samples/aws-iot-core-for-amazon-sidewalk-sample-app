// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { ReactNode, createContext, useContext, useEffect, useState } from 'react';
import { apiClient, setAuthHeader, setUsernameHeader } from '../apiClient';
import { ENDPOINTS } from '../endpoints';
import { logger } from '../utils/logger';
import toast from 'react-hot-toast';
import { ACCESS_TOKEN, UNAUTHORIZE } from '../constants';
import { useNavigate } from 'react-router';
import { Routes } from '../routes';

const authContext = createContext({
  isAuthorized: false,
  login: (_username: string, _password: string) => {},
  isLogginIn: false
});

export const useAuth = () => useContext(authContext);

export const useAuthProvider = () => {
  const [isLogginIn, setIsLogginIn] = useState(false);
  const [isAuthorized, setIsAuthorized] = useState(() => !!localStorage.getItem(ACCESS_TOKEN));
  const [shouldRedirect, setShouldRedirect] = useState(false);
  const navigate = useNavigate();

  const login = async (username: string, password: string) => {
    setIsLogginIn(true);
    try {
      setUsernameHeader(username);
      const response: string = await apiClient.post(ENDPOINTS.login, {
        username,
        password
      });
      setAuthHeader(response);
      setIsAuthorized(true);
      setShouldRedirect(true);
    } catch (error) {
      logger.log('error during login', error);
      toast.error('User or password incorrect');
    } finally {
      setIsLogginIn(false);
    }
  };

  // check for auth error var to show a message in case user gets logged out
  useEffect(() => {
    if (localStorage.getItem(UNAUTHORIZE)) {
      setTimeout(() => {
        toast.error('Unauthorize error');
        localStorage.removeItem(UNAUTHORIZE);
      }, 0);
    }
  }, []);

  useEffect(() => {
    if (shouldRedirect) {
      navigate(Routes.sensorMonitoring);
    }
  }, [isAuthorized]);

  return {
    isAuthorized,
    login,
    isLogginIn
  };
};

export const ProvideAuth = ({ children }: { children: ReactNode }) => {
  const auth = useAuthProvider();

  return <authContext.Provider value={auth}>{children}</authContext.Provider>;
};
