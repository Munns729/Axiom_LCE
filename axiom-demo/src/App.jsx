import React from 'react';
import InteractiveDealVerifier from './InteractiveDealVerifier';
import './App.css';
import { Toaster } from 'sonner';

function App() {
  return (
    <div className="App">
      <InteractiveDealVerifier />
      <Toaster position="top-right" richColors />
    </div>
  );
}

export default App;
