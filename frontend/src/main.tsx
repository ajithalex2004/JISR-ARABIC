import React from 'react';
import ReactDOM from 'react-dom/client';
import { Root } from './entry/Root';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { UpdateAvailableBanner } from './components/common/UpdateAvailableBanner';
import './index.css';

ReactDOM.createRoot(document.getElementById('app')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <Root />
      <UpdateAvailableBanner />
    </ErrorBoundary>
  </React.StrictMode>
);
