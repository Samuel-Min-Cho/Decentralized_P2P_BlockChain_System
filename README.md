# Full-Stack React + Node.js Project

This is a basic full-stack project with a **React frontend** and a **Node.js Express backend**.

## 📁 Project Structure
```
full-stack-react-node/
│-- frontend/        # React Frontend
│   ├── src/        
│   ├── src/components/ 
│   ├── src/App.jsx 
│   ├── src/main.jsx
│   ├── src/index.css
│-- backend/         # Node.js Backend
│   ├── server.js 
│-- package.json (for backend dependencies)
│-- README.md
```

## 🚀 How to Run the Project

### 1️⃣ Install Dependencies

#### Backend (Node.js)
```sh
cd backend
npm install express cors
```

#### Frontend (React)
```sh
cd frontend
npm install
```

### 2️⃣ Start the Backend Server
```sh
cd backend
node server.js
```
The backend runs on **http://localhost:5000/**.

### 3️⃣ Start the Frontend (React)
```sh
cd frontend
npm run dev
```
The frontend runs on **http://localhost:5173/**.

### 🔄 API Endpoint Test
Open your browser and go to:
- **Backend Root**: [http://localhost:5000/](http://localhost:5000/)
- **API Data Endpoint**: [http://localhost:5000/api/data](http://localhost:5000/api/data)

If everything is working, the React frontend will display data from the backend.

## 📌 Features
✅ React frontend with routing  
✅ Node.js Express backend with API endpoints  
✅ CORS enabled for frontend-backend communication  

---
### 📩 Need Help?
If you have any issues, feel free to ask for support! 🚀
