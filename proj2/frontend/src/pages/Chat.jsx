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
  const [refiningUseCase, setRefiningUseCase] = useState(null);
  const [refineType, setRefineType] = useState('more_main_flows');
  const [refining, setRefining] = useState(false);
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
      // Get fresh use cases from database (includes refined versions)
      const freshUseCases = response.data.generated_use_cases || [];
      
      // Create a map of fresh use cases by ID for quick lookup
      const freshUseCasesMap = new Map();
      freshUseCases.forEach(uc => {
        if (uc.id) {
          freshUseCasesMap.set(uc.id, uc);
        }
      });
      
      // Filter out parsed document text that appears after document uploads
      const formattedMessages = [];
      for (let i = 0; i < history.length; i++) {
        const msg = history[i];
        const prevMsg = i > 0 ? history[i - 1] : null;
        
        // Check if this is a long text message that follows a document upload
        // The backend stores parsed text with metadata.type='requirement_input' even from documents
        const isLongText = msg.role === 'user' && 
                          msg.content && 
                          msg.content.length > 200; // Long text (likely parsed document content)
        
        const prevWasDocumentUpload = prevMsg && 
                                     prevMsg.metadata?.type === 'document_upload';
        
        // Skip long text messages that follow document uploads (these are the parsed text)
        // Regular text inputs are usually shorter, so this filters out document parsed content
        if (isLongText && prevWasDocumentUpload && msg.metadata?.type !== 'document_upload') {
          continue;
        }
        
        // For use cases, replace old metadata with fresh data from database
        let useCases = undefined;
        if (Array.isArray(msg.metadata?.use_cases)) {
          useCases = msg.metadata.use_cases.map(uc => {
            const ucId = uc.id || uc.use_case_id;
            // If we have fresh data from database, use it instead of old metadata
            if (ucId && freshUseCasesMap.has(ucId)) {
              return freshUseCasesMap.get(ucId);
            }
            // Fallback to metadata if not found in fresh data
            return {
              ...uc,
              id: ucId || undefined,
            };
          });
        }
        
        formattedMessages.push({
          role: msg.role,
          content: msg.content,
          metadata: msg.metadata,
          // Use fresh use cases from database instead of stale metadata
          results: useCases,
          validation_results: Array.isArray(msg.metadata?.validation_results) ? msg.metadata.validation_results : undefined,
        });
      }
      
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
      content: '',
      metadata: {
        type: 'document_upload',
        filename: file.name,
        size: file.size,
      },
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

  // Handle use case refinement
  const handleRefineUseCase = async (useCaseId, refinementType) => {
    setRefining(true);
    toast.info('Refining use case...', { autoClose: 2000 });
    
    try {
      const response = await api.refineUseCase({
        use_case_id: useCaseId,
        refinement_type: refinementType,
      });

      console.log('Refinement response:', response.data);
      const refinedData = response.data.refined_use_case;
      
      toast.success('✨ Use case refined successfully! Refreshing...');
      
      // Wait a moment for backend to finish updating
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Always reload from database to get the latest refined data
      if (currentSessionId) {
        await loadConversationHistory();
      } else {
        // Fallback: update current messages if no session
        setMessages(prevMessages => {
          return prevMessages.map(msg => {
            if (msg.results && Array.isArray(msg.results)) {
              return {
                ...msg,
                results: msg.results.map(uc => {
                  if (uc.id === useCaseId) {
                    console.log('Updating use case with refined data:', refinedData);
                    // Update with refined data from response
                    return {
                      ...uc,
                      ...refinedData,
                      id: useCaseId, // Preserve the id
                      _refined: true, // Mark as refined for visual feedback
                    };
                  }
                  return uc;
                }),
              };
            }
            return msg;
          });
        });
      }
      
      setRefiningUseCase(null);
      setRefineType('more_main_flows');
      
      // Scroll to show the refined use case
      setTimeout(() => {
        scrollToBottom();
      }, 100);
      
    } catch (error) {
      console.error('Refinement error:', error);
      toast.error(error.response?.data?.detail || 'Failed to refine use case. Please try again.');
    } finally {
      setRefining(false);
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
            {messages.map((message, idx) => {
              // Skip long parsed text messages that follow document uploads
              // The backend stores parsed text with metadata.type='requirement_input' even from documents
              const prevMsg = idx > 0 ? messages[idx - 1] : null;
              const isLongParsedText = message.role === 'user' && 
                                      message.content && 
                                      message.content.length > 200 &&
                                      message.metadata?.type !== 'document_upload' &&
                                      prevMsg?.metadata?.type === 'document_upload';
              
              if (isLongParsedText) {
                return null; // Don't render parsed text from document uploads
              }
              
              return (
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
                  {/* Pretty file upload pill for user file messages */}
                  {message.metadata?.type === 'document_upload' ? (
                    <div className={`flex items-center gap-3 ${message.role === 'user' ? 'text-white' : 'text-gray-900'}`}>
                      <div className={`flex items-center justify-center w-9 h-9 rounded-md ${message.role === 'user' ? 'bg-white/15' : 'bg-indigo-100 text-indigo-700'}`}>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                          <path d="M19.5 8.25v9.75A2.25 2.25 0 0 1 17.25 20.25H6.75A2.25 2.25 0 0 1 4.5 18V6A2.25 2.25 0 0 1 6.75 3.75h6.939a2.25 2.25 0 0 1 1.591.659l3.061 3.061a2.25 2.25 0 0 1 .659 1.591z"/>
                          <path d="M14.25 3.75v3.75a.75.75 0 0 0 .75.75h3.75"/>
                        </svg>
                      </div>
                      <div className="min-w-0">
                        <div className={`font-medium ${message.role === 'user' ? 'text-white' : 'text-gray-900'}`}>
                          {message.metadata.filename}
                        </div>
                        {typeof message.metadata.size === 'number' && (
                          <div className={`text-xs ${message.role === 'user' ? 'text-white/80' : 'text-gray-500'}`}>
                            {(message.metadata.size / 1024).toFixed(1)} KB
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    message.content && !/^\s*Smart extraction:/i.test(message.content) && !/^\s*✅ Extracted/i.test(message.content) && (
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    )
                  )}

                  {message.results && message.results.length > 0 && (
                    <div className="mt-4 space-y-4">
                      {message.results.map((uc, i) => {
                        const validation = message.validation_results?.find(
                          v => v.title === uc.title
                        );
                        
                        // Debug: Log use case structure to help identify missing id
                        if (i === 0) {
                          console.log('Use case structure:', { id: uc.id, title: uc.title, status: uc.status });
                        }

                        return (
                          <div 
                            key={i} 
                            className={`bg-gray-50 border rounded-lg p-4 text-gray-900 ${
                              uc._refined ? 'border-green-400 bg-green-50' : ''
                            } transition-all duration-300`}
                          >
                            {/* Title and Status - NO WARNINGS HERE */}
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-2">
                                <p className="font-bold text-lg">{uc.title}</p>
                                {uc._refined && (
                                  <span className="text-xs px-2 py-1 bg-green-200 text-green-800 rounded-full">
                                    ✨ Refined
                                  </span>
                                )}
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

                            {/* Refine Button - Show for all stored use cases */}
                            <div className="mt-4 pt-3 border-t border-gray-200">
                              {uc.id ? (
                                <div className="flex items-center gap-2">
                                  <button
                                    onClick={() => setRefiningUseCase(uc.id)}
                                    className="text-sm px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
                                    disabled={refining || refiningUseCase === uc.id}
                                  >
                                    {refining && refiningUseCase === uc.id ? (
                                      <span className="flex items-center gap-1">
                                        <span className="animate-spin">⏳</span> Refining...
                                      </span>
                                    ) : (
                                      '✨ Refine Use Case'
                                    )}
                                  </button>
                                  {refining && refiningUseCase === uc.id && (
                                    <span className="text-xs text-gray-500">
                                      Processing refinement...
                                    </span>
                                  )}
                                </div>
                              ) : (
                                <p className="text-xs text-gray-500">
                                  💡 Refinement available for stored use cases only
                                </p>
                              )}
                            </div>

                            {/* ✅ NO VALIDATION WARNINGS SECTION HERE - COMPLETELY REMOVED */}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
              );
            })}

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

      {/* Refine Use Case Modal */}
      {refiningUseCase && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Refine Use Case</h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Refinement Type
              </label>
              <select
                value={refineType}
                onChange={(e) => setRefineType(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="more_main_flows">Refine Main Flows</option>
                <option value="more_sub_flows">Refine Sub Flows</option>
                <option value="more_alternate_flows">Refine Alternate Flows</option>
                <option value="more_preconditions">Refine Preconditions</option>
                <option value="more_stakeholders">Refine Stakeholders</option>
              </select>
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setRefiningUseCase(null);
                  setRefineType('more_main_flows');
                }}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
                disabled={refining}
              >
                Cancel
              </button>
              <button
                onClick={() => handleRefineUseCase(refiningUseCase, refineType)}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                disabled={refining}
              >
                {refining ? (
                  <>
                    <span className="animate-spin">⏳</span>
                    <span>Refining...</span>
                  </>
                ) : (
                  <>
                    <span>✨</span>
                    <span>Refine</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

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