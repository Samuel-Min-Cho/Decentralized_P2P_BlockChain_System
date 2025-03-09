import { useState, useEffect } from "react";

function Home() {
  const [count, setCount] = useState(0);
  const [backendData, setBackendData] = useState("");

  useEffect(() => {
    fetch("http://localhost:5000/api/data")
      .then((response) => response.json())
      .then((data) => setBackendData(data.data));
  }, []);

  return (
    <div style={{ textAlign: "center", marginTop: "20px" }}>
      <h1>Welcome to Home Page</h1>
      <p>Counter: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increase</button>
      <h3>Backend Response:</h3>
      <p>{backendData}</p>
    </div>
  );
}

export default Home;