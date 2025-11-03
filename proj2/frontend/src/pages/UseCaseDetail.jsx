import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { toast } from 'react-toastify';
import LoadingSpinner from '../components/LoadingSpinner';
import QualityBadge from '../components/QualityBadge';

function UseCaseDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [useCase, setUseCase] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUseCase();
  }, [id]);

  const loadUseCase = async () => {
    // Note: You'll need to add this endpoint to your backend
    // For now, we'll simulate it
    setLoading(false);
    toast.info('Use case detail view - endpoint needed');
  };

  if (loading) return <LoadingSpinner message="Loading use case..." />;

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => navigate(-1)}
          className="mb-4 text-primary hover:underline"
        >
          ← Back
        </button>

        <div className="bg-white rounded-lg shadow-sm border p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Use Case Detail
          </h1>
          
          <p className="text-gray-600">
            Detailed view and editing functionality coming soon...
          </p>
        </div>
      </div>
    </div>
  );
}

export default UseCaseDetail;