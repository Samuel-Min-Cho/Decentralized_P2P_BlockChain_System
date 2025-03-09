import { Link } from "react-router-dom";

function Header() {
  return (
    <nav style={{ padding: "10px", background: "#282c34", color: "white" }}>
      <Link to="/" style={{ marginRight: "10px", color: "white" }}>Home</Link>
      <Link to="/about" style={{ color: "white" }}>About</Link>
    </nav>
  );
}

export default Header;