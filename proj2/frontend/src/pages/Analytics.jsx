import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../store/useSessionStore';
import LoadingSpinner from '../components/LoadingSpinner';

function Analytics() {
  const { currentSessionId } = useSessionStore();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (currentSessionId) {
      loadMetrics();
    } else {
      setLoading(false);
    }
  }, [currentSessionId]);

  const loadMetrics = async () => {
    try {
      const response = await api.getMetrics(currentSessionId);
      setMetrics(response.data);
    } catch (error) {
      toast.error('Failed to load metrics');
    } finally {
      setLoading(false);
    }
  };

  if (!currentSessionId) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <p className="text-yellow-800">
              Please select a session or create a new one to view analytics
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) return <LoadingSpinner message="Loading analytics..." />;

  if (!metrics || metrics.total_use_cases === 0) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">
            Analytics 📊
          </h1>
          <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
            <p className="text-gray-500">No use cases to analyze yet</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Analytics 📊
        </h1>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <p className="text-gray-500 text-sm">Total Use Cases</p>
            <p className="text-3xl font-bold text-gray-900">
              {metrics.total_use_cases}
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <p className="text-gray-500 text-sm">Avg Main Flow Steps</p>
            <p className="text-3xl font-bold text-gray-900">
              {metrics.averages.main_flow_steps}
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <p className="text-gray-500 text-sm">Completeness Score</p>
            <p className="text-3xl font-bold text-green-600">
              {metrics.completeness_score}%
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <p className="text-gray-500 text-sm">Conflicts</p>
            <p className="text-3xl font-bold text-red-600">
              {metrics.conflicts?.length || 0}
            </p>
          </div>
        </div>

        {/* Quality Summary */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Quality Distribution
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-600 font-semibold mb-2">Excellent</p>
              <p className="text-3xl font-bold text-green-700">
                {metrics.quality_summary.excellent}
              </p>
              <p className="text-sm text-green-600 mt-1">Score ≥ 80</p>
            </div>

            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-yellow-600 font-semibold mb-2">Good</p>
              <p className="text-3xl font-bold text-yellow-700">
                {metrics.quality_summary.good}
              </p>
              <p className="text-sm text-yellow-600 mt-1">Score 60-79</p>
            </div>

            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 font-semibold mb-2">Needs Improvement</p>
              <p className="text-3xl font-bold text-red-700">
                {metrics.quality_summary.needs_improvement}
              </p>
              <p className="text-sm text-red-600 mt-1">Score &lt; 60</p>
            </div>
          </div>
        </div>

        {/* Coverage */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Coverage</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-gray-600">With Sub Flows</span>
                <span className="font-semibold">
                  {metrics.coverage.sub_flows_percentage}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: `${metrics.coverage.sub_flows_percentage}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <span className="text-gray-600">With Alternate Flows</span>
                <span className="font-semibold">
                  {metrics.coverage.alternate_flows_percentage}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: `${metrics.coverage.alternate_flows_percentage}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Stakeholders */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Stakeholders</h2>
          <div className="flex flex-wrap gap-2">
            {metrics.stakeholders.map((stakeholder, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm"
              >
                {stakeholder}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;