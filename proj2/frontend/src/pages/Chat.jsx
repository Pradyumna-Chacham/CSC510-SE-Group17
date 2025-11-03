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

  if (!currentSessionId) {  
    setCurrentSession(response.data.session_id);  
  }  

  const assistantMessage = {  
    role: 'assistant',  
    content: `✅ Extracted ${response.data.extracted_count} use cases in ${response.data.processing_time_seconds}s`,  
    results: response.data.results,  
    validation_results: response.data.validation_results,  
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

  if (!currentSessionId) {  
    setCurrentSession(response.data.session_id);  
  }  

  const assistantMessage = {  
    role: 'assistant',  
    content: `✅ Extracted ${response.data.extracted_count} use cases from ${file.name}`,  
    results: response.data.results,  
    validation_results: response.data.validation_results,  
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

return ( <div className="h-full flex flex-col bg-gray-50"> <div className="flex-1 overflow-y-auto p-6">
{messages.length === 0 ? ( <div className="max-w-3xl mx-auto text-center py-20"> <h1 className="text-4xl font-bold text-gray-900 mb-4">
Welcome to ReqEngine 🚀 </h1> <p className="text-lg text-gray-600 mb-8">
Transform unstructured requirements into structured use cases </p> <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left"> <div className="bg-white p-4 rounded-lg border"> <p className="font-semibold text-gray-900 mb-2">💡 Example:</p> <p className="text-sm text-gray-600">
"User can login to the system. User can search for products and add items to cart." </p> </div> <div className="bg-white p-4 rounded-lg border"> <p className="font-semibold text-gray-900 mb-2">📄 Or upload:</p> <p className="text-sm text-gray-600">
PDF, DOCX, TXT, or MD files with your requirements </p> </div> </div> </div>
) : ( <div className="max-w-4xl mx-auto space-y-6 pb-4">
{messages.map((message, idx) => (
<div key={idx} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
<div className={`max-w-3xl rounded-lg p-4 ${message.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-white border'}`}> <p className="whitespace-pre-wrap">{message.content}</p>

```
              {message.results && message.results.length > 0 && (  
                <div className="mt-4 space-y-2">  
                  {message.results.map((uc, i) => (  
                    <div key={i} className="bg-gray-50 border rounded p-3 text-gray-900">  
                      <p className="font-medium">{uc.title}</p>  
                      <span className={`text-xs px-2 py-1 rounded-full inline-block mt-1 ${uc.status === 'stored' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>  
                        {uc.status === 'stored' ? '✅ Stored' : '🔄 Duplicate'}  
                      </span>  
                    </div>  
                  ))}  
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
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>  
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>  
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
          <button onClick={() => setShowFileUpload(false)} className="mt-2 text-sm text-gray-600 hover:text-gray-900">  
            ← Back to text input  
          </button>  
        </div>  
      ) : (  
        <div className="flex gap-2 items-end">  
          <button onClick={() => setShowFileUpload(true)} disabled={loading} className="p-3 text-gray-600 hover:bg-gray-100 rounded-lg transition disabled:opacity-50 flex-shrink-0" title="Upload file">  
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">  
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/>  
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

          <button onClick={handleSendText} disabled={loading || !inputText.trim()} className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium flex-shrink-0">  
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
