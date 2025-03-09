const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());

app.get("/", (req, res) => {
  res.send({ message: "Hello from Node.js backend!" });
});

app.get("/api/data", (req, res) => {
  res.json({ data: "This is data from the backend" });
});

const PORT = 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));