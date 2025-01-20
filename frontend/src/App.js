import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import BookList from "./pages/BookList";
import AuthorList from "./pages/AuthorList";
import AuthorDetail from "./pages/AuthorDetail";  // Import the new AuthorDetail page

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/books" element={<BookList />} />
                <Route path="/authors" element={<AuthorList />} />
                <Route path="/author/:authorId" element={<AuthorDetail />} />  {/* New route for AuthorDetail */}
            </Routes>
        </Router>
    );
};

export default App;
