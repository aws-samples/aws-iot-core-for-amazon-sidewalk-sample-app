// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Header } from './components/Header/Header';
import { Suspense, useEffect, useState } from 'react';
import { Spinner } from './components/Spinner/Spinner';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import { Routes } from './routes';
import { QueryClient, QueryClientProvider } from 'react-query';
import './App.css';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false
    }
  }
});

function App() {
  const { isAuthorized } = useAuth();
  const navigate = useNavigate();
  const [isFirstLoad, setIsFirstLoad] = useState(true);

  useEffect(() => {
    setIsFirstLoad(false);
    if (isAuthorized) return;
    navigate(Routes.auth);
  }, [isAuthorized]);

  // added to avoid flickering while checking for the auth
  if (isFirstLoad) return <></>;

  return (
    <div className="App">
      <Header />
      <Suspense fallback={<Spinner />}>
        <QueryClientProvider client={queryClient}>
          <Outlet />
        </QueryClientProvider>
      </Suspense>
    </div>
  );
}

export default App;
