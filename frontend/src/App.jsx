import React, { useState } from 'react';

function App() {
  const [sender, setSender] = useState("UserA");
  const [recipient, setRecipient] = useState("UserB");
  const [amount, setAmount] = useState(25);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResponse(null);

    const tx = {
      sender,
      recipient,
      amount: parseFloat(amount)
    };

    try {
      const res = await fetch("http://localhost:8000/transaction", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(tx)
      });

      if (!res.ok) {
        throw new Error(`Error ${res.status}`);
      }

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error("Transaction error:", err);
      setError("Transaction failed. Check backend logs.");
    }
  };

  const handleReset = async () => {
    if (!window.confirm("Reset blockchain and database?")) return;

    try {
      const res = await fetch("http://localhost:8000/reset", {
        method: "POST"
      });

      if (!res.ok) throw new Error("Reset failed");

      const data = await res.json();
      alert(data.status || "Reset successful.");
      setResponse(null);
      setError(null);
    } catch (err) {
      console.error("Reset error:", err);
      alert("Failed to reset.");
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "1rem" }}>
        <button
          onClick={handleReset}
          style={{
            padding: "0.5rem 1rem",
            background: "#ff4d4d",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer"
          }}
        >
          🔄 Reset Blockchain
        </button>
      </div>

      <h1>Blockchain Transaction</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Sender: </label>
          <input value={sender} onChange={(e) => setSender(e.target.value)} />
        </div>
        <div>
          <label>Recipient: </label>
          <input value={recipient} onChange={(e) => setRecipient(e.target.value)} />
        </div>
        <div>
          <label>Amount: </label>
          <input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
        </div>
        <button type="submit" style={{ marginTop: "1rem" }}>Send Transaction</button>
      </form>

      {error && (
        <div style={{ marginTop: "2rem", color: "red" }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {response && (
        <div style={{ marginTop: "2rem" }}>
          <h3>Server Response:</h3>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
