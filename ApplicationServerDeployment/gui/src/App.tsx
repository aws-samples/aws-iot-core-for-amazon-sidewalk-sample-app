// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Header } from "./components/Header/Header";
import { DevicesWrapper } from "./components/DevicesWrapper/DevicesWrapper";
import "./App.css";

function App() {
  return (
    <div className="App">
      <Header />
      <DevicesWrapper />
    </div>
  );
}

export default App;
