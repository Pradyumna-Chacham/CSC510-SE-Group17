import { useEffect, useState } from "react";
import axios from "axios";
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");

  const handleSend = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/llm", { text: prompt });
      setResponse(res.data.response);
    } catch (err) {
      console.error(err);
      setResponse("Error fetching response");
    }
  };

  return (
    <div className="p-8">
      <textarea
        rows={4}
        className="w-full border rounded p-2"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Type your prompt here..."
      />
      <button className="mt-2 px-4 py-2 bg-blue-600 text-white rounded" onClick={handleSend}>
        Send
      </button>
      <div className="mt-4 p-4 border rounded bg-gray-100">
        <strong>Response:</strong>
        <p>{response}</p>
      </div>
    </div>
  );
}

export default App;
