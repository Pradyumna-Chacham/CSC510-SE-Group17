import React, { useState, useRef, useEffect } from 'react';
import { api } from '../api/client';
import { toast } from 'react-toastify';
import useSessionStore from '../store/useSessionStore';
import FileUploader from '../components/FileUploader';

function Chat() {
  const { currentSessionId, setCurrentSession } = useSessionStore();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const messagesEndRef = useRef(null);

  // Normalize backend extraction response for consistent rendering
  const normalizeExtractionResponse = (data) => {
    const resultsArray = Array.isArray(data?.results)
      ? data.results
      : Array.isArray(data?.generated_use_cases)
      ? data.generated_use_cases
      : [];

    const normalizedResults = resultsArray.map((uc) => ({
      status: uc.status || 'stored',
      id: uc.id,
      title: uc.title || 'Untitled',
      preconditions: Array.isArray(uc.preconditions) ? uc.preconditions : [],
      main_flow: Array.isArray(uc.main_flow) ? uc.main_flow : Array.isArray(uc.main_flows) ? uc.main_flows.flat() : [],
      sub_flows: Array.isArray(uc.sub_flows) ? uc.sub_flows : [],
      alternate_flows: Array.isArray(uc.alternate_flows) ? uc.alternate_flows : [],
      outcomes: Array.isArray(uc.outcomes) ? uc.outcomes : [],
      stakeholders: Array.isArray(uc.stakeholders) ? uc.stakeholders : [],
    }));

    return {
      message: data?.message,
      session_id: data?.session_id,
      extracted_count: Number.isFinite(data?.extracted_count) ? data.extracted_count : normalizedResults.length,
      processing_time_seconds: data?.processing_time_seconds,
      validation_results: Array.isArray(data?.validation_results) ? data.validation_results : [],
      results: normalizedResults,
    };
  };

  // ✅ VERIFICATION: This will prove the new code is loaded
  useEffect(() => {
    console.log("🚀 NEW CHAT COMPONENT LOADED - v2.0");
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (currentSessionId) {
      loadConversationHistory();
    } else {
      setMessages([]);
    }
  }, [currentSessionId]);

  const loadConversationHistory = async () => {
    try {
      const response = await api.getSessionHistory(currentSessionId, 50);
      const history = response.data.conversation_history || [];
      const formattedMessages = history.map(msg => ({
        role: msg.role,
        content: msg.content,
        metadata: msg.metadata,
        // When assistant stored metadata, surface use cases for rendering
        results: Array.isArray(msg.metadata?.use_cases) ? msg.metadata.use_cases : undefined,
        validation_results: Array.isArray(msg.metadata?.validation_results) ? msg.metadata.validation_results : undefined,
      }));
      setMessages(formattedMessages);
    } catch (error) {
      console.log('Could not load history');
    }
  };

  const handleSendText = async () => {
    if (!inputText.trim()) {
      toast.error('Please enter some text');
      return;
    }

    const userMessage = {
      role: 'user',
      content: inputText,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);

    try {
      const response = await api.extractFromText({
        raw_text: inputText,
        session_id: currentSessionId || undefined,
      });
      const normalized = normalizeExtractionResponse(response.data);

      if (!currentSessionId) {
        setCurrentSession(normalized.session_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: `✅ Extracted ${normalized.extracted_count} use cases in ${normalized.processing_time_seconds}s`,
        results: normalized.results,
        validation_results: normalized.validation_results,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      toast.success('Use cases extracted!');
    } catch (error) {
      console.error('Extraction error:', error);
      const errorMessage = {
        role: 'assistant',
        content: '⚠ Could not process request. Make sure backend is running.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    const userMessage = {
      role: 'user',
      content: `📄 Uploaded file: ${file.name}`,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setShowFileUpload(false);

    const formData = new FormData();
    formData.append('file', file);
    if (currentSessionId) formData.append('session_id', currentSessionId);

    try {
      const response = await api.extractFromDocument(formData);
      const normalized = normalizeExtractionResponse(response.data);

      if (!currentSessionId) {
        setCurrentSession(normalized.session_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: `✅ Extracted ${normalized.extracted_count} use cases from ${file.name}`,
        results: normalized.results,
        validation_results: normalized.validation_results,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      toast.success('Document processed!');
    } catch (error) {
      console.error('Upload error:', error);
      const errorMessage = {
        role: 'assistant',
        content: '⚠ Could not process file. Make sure backend is running.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendText();
    }
  };

  // Get quality badge color
  const getQualityBadge = (validation) => {
    if (!validation) return null;
    
    const score = validation.quality_score || 0;
    
    if (score >= 80) {
      return <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
        ✨ {score}/100
      </span>;
    } else if (score >= 60) {
      return <span className="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-700">
        ⚠️ {score}/100
      </span>;
    } else {
      return <span className="text-xs px-2 py-1 rounded-full bg-red-100 text-red-700">
        ❌ {score}/100
      </span>;
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <div className="max-w-3xl mx-auto text-center py-20">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Welcome to ReqEngine 🚀
            </h1>
            <p className="text-lg text-gray-600 mb-8">
              Transform unstructured requirements into structured use cases
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
              <div className="bg-white p-4 rounded-lg border">
                <p className="font-semibold text-gray-900 mb-2">💡 Example:</p>
                <p className="text-sm text-gray-600">
                  "User can login to the system. User can search for products and add items to cart."
                </p>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <p className="font-semibold text-gray-900 mb-2">📄 Or upload:</p>
                <p className="text-sm text-gray-600">
                  PDF, DOCX, TXT, or MD files with your requirements
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-6 pb-4">
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white border'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>

                  {message.results && message.results.length > 0 && (
                    <div className="mt-4 space-y-4">
                      {message.results.map((uc, i) => {
                        const validation = message.validation_results?.find(
                          v => v.title === uc.title
                        );

                        return (
                          <div key={i} className="bg-gray-50 border rounded-lg p-4 text-gray-900">
                            {/* Title and Status - NO WARNINGS HERE */}
                            <div className="flex items-center justify-between mb-3">
                              <p className="font-bold text-lg">{uc.title}</p>
                              <div className="flex gap-2">
                                <span
                                  className={`text-xs px-2 py-1 rounded-full ${
                                    uc.status === 'stored'
                                      ? 'bg-green-100 text-green-700'
                                      : 'bg-yellow-100 text-yellow-700'
                                  }`}
                                >
                                  {uc.status === 'stored' ? '✅ Stored' : '🔄 Duplicate'}
                                </span>
                                {getQualityBadge(validation)}
                              </div>
                            </div>

                            {/* Preconditions */}
                            {uc.preconditions && uc.preconditions.length > 0 && (
                              <div className="mb-3">
                                <p className="font-semibold text-indigo-700 mb-1">📋 Preconditions:</p>
                                <ul className="list-disc list-inside ml-2 space-y-1">
                                  {uc.preconditions.map((pre, idx) => (
                                    <li key={idx} className="text-sm text-gray-700">
                                      {pre}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Main Flow */}
                            {uc.main_flow && uc.main_flow.length > 0 && (
                              <div className="mb-3">
                                <p className="font-semibold text-indigo-700 mb-1">🔄 Main Flow:</p>
                                <ol className="list-decimal list-inside ml-2 space-y-1">
                                  {uc.main_flow.map((step, idx) => (
                                    <li key={idx} className="text-sm text-gray-700">
                                      {step}
                                    </li>
                                  ))}
                                </ol>
                              </div>
                            )}

                            {/* Sub Flows */}
                            {uc.sub_flows && uc.sub_flows.length > 0 && (
                              <div className="mb-3">
                                <p className="font-semibold text-indigo-700 mb-1">🔀 Sub Flows:</p>
                                <ul className="list-disc list-inside ml-2 space-y-1">
                                  {uc.sub_flows.map((sub, idx) => (
                                    <li key={idx} className="text-sm text-gray-700">
                                      {sub}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Alternate Flows */}
                            {uc.alternate_flows && uc.alternate_flows.length > 0 && (
                              <div className="mb-3">
                                <p className="font-semibold text-indigo-700 mb-1">⚠️ Alternate Flows:</p>
                                <ul className="list-disc list-inside ml-2 space-y-1">
                                  {uc.alternate_flows.map((alt, idx) => (
                                    <li key={idx} className="text-sm text-gray-700">
                                      {alt}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Outcomes */}
                            {uc.outcomes && uc.outcomes.length > 0 && (
                              <div className="mb-3">
                                <p className="font-semibold text-indigo-700 mb-1">✅ Outcomes:</p>
                                <ul className="list-disc list-inside ml-2 space-y-1">
                                  {uc.outcomes.map((outcome, idx) => (
                                    <li key={idx} className="text-sm text-gray-700">
                                      {outcome}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Stakeholders */}
                            {uc.stakeholders && uc.stakeholders.length > 0 && (
                              <div>
                                <p className="font-semibold text-indigo-700 mb-1">👥 Stakeholders:</p>
                                <div className="flex flex-wrap gap-2">
                                  {uc.stakeholders.map((stakeholder, idx) => (
                                    <span
                                      key={idx}
                                      className="text-xs px-2 py-1 bg-indigo-100 text-indigo-700 rounded-full"
                                    >
                                      {stakeholder}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* ✅ NO VALIDATION WARNINGS SECTION HERE - COMPLETELY REMOVED */}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border rounded-lg p-4">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: '0.1s' }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: '0.2s' }}
                    ></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="border-t bg-white p-4 flex-shrink-0">
        <div className="max-w-4xl mx-auto">
          {showFileUpload ? (
            <div>
              <FileUploader onFileSelect={handleFileUpload} uploading={loading} />
              <button
                onClick={() => setShowFileUpload(false)}
                className="mt-2 text-sm text-gray-600 hover:text-gray-900"
              >
                ← Back to text input
              </button>
            </div>
          ) : (
            <div className="flex gap-2 items-end">
              <button
                onClick={() => setShowFileUpload(true)}
                disabled={loading}
                className="p-3 text-gray-600 hover:bg-gray-100 rounded-lg transition disabled:opacity-50 flex-shrink-0"
                title="Upload file"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
                  />
                </svg>
              </button>

              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe your requirements... (Press Enter to send, Shift+Enter for new line)"
                className="flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                rows={2}
                disabled={loading}
              />

              <button
                onClick={handleSendText}
                disabled={loading || !inputText.trim()}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium flex-shrink-0"
              >
                {loading ? '⏳' : '📤'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Chat;