import React from 'react';

function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div data-testid="loading-spinner" className="flex flex-col items-center justify-center p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  );
}

export default LoadingSpinner;