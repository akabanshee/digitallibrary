import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Typography, Button, Grid, TextField, Box, MenuItem } from "@mui/material";

const ManageBooks = () => {
    const [books, setBooks] = useState([]);
    const [showAddForm, setShowAddForm] = useState(false);
    const [newBook, setNewBook] = useState({
    
        title: "",
        year: "",
        category: "",
        author_id: "",
        pricing: "",
    });
    const [filterYear, setFilterYear] = useState(""); // Yıl filtresi için state

    useEffect(() => {
        fetchBooks();
    }, []);

    const fetchBooks = async () => {
        try {
            const response = await axios.get("/books");
            setBooks(response.data);
        } catch (error) {
            console.error("Error fetching books:", error);
        }
    };

    const handleAddBook = async () => {
        try {
            await axios.post("/books", newBook);
            fetchBooks();
            setShowAddForm(false);
            setNewBook({ title: "", year: "", category: "", author_id: "", pricing: "" });
        } catch (error) {
            console.error("Error adding book:", error);
        }
    };

    const handleChange = (e) => {
        setNewBook({ ...newBook, [e.target.name]: e.target.value });
    };

    // Yıl filtresi için yeni fonksiyon
    const handleFilterByYear = () => {
        if (!filterYear) {
            alert("Please enter a year to filter!");
            return;
        }
        fetchBooks(filterYear); // API'den yıl filtresiyle kitapları getir
    };

     // Filtreyi temizlemek için fonksiyon
    const handleClearFilter = () => {
        setFilterYear(""); // Yıl filtresini sıfırla
        fetchBooks(); // Tüm kitapları tekrar getir
    };

    return (
        <Container maxWidth="md">
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
                <Typography variant="h4">Manage Books</Typography>
                <Button variant="contained" color="primary" onClick={() => setShowAddForm(!showAddForm)}>
                    + Add Book
                </Button>
            </Box>

            {/* Yıl filtresi formu */}
            <Box display="flex" alignItems="center" mb={4}>
                <TextField
                    label="Filter by Year"
                    type="number"
                    value={filterYear}
                    onChange={(e) => setFilterYear(e.target.value)}
                    style={{ marginRight: "10px" }}
                />
                <Button
                    variant="contained"
                    color="primary"
                    onClick={handleFilterByYear}
                    style={{ marginRight: "10px" }}
                >
                    Filter
                </Button>
                <Button variant="outlined" color="secondary" onClick={handleClearFilter}>
                    Clear
                </Button>
            </Box>

            {showAddForm ? (
                <Box component="form" noValidate autoComplete="off" mb={4}>
                    <Typography variant="h6" mb={2}>Add a New Book</Typography>
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Title"
                                name="title"
                                value={newBook.title}
                                onChange={handleChange}
                                required
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                fullWidth
                                label="Year"
                                name="year"
                                value={newBook.year}
                                onChange={handleChange}
                                type="number"
                                required
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                select
                                fullWidth
                                label="Category"
                                name="category"
                                value={newBook.category}
                                onChange={handleChange}
                                required
                            >
                                <MenuItem value="Bilim Kurgu">Science Fiction</MenuItem>
                                <MenuItem value="Otobiyografi">Autobiography</MenuItem>
                                <MenuItem value="Drama">Drama</MenuItem>
                                <MenuItem value="Biyografi">Biography</MenuItem>
                                <MenuItem value="Roman">Novel</MenuItem>
                                <MenuItem value="Siir">Poem</MenuItem>
                            </TextField>
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                fullWidth
                                label="Author ID"
                                name="author_id"
                                value={newBook.author_id}
                                onChange={handleChange}
                                type="number"
                                required
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                fullWidth
                                label="Pricing"
                                name="pricing"
                                value={newBook.pricing}
                                onChange={handleChange}
                                type="number"
                                required
                            />
                        </Grid>
                    </Grid>
                    <Box mt={2}>
                        <Button variant="contained" color="success" onClick={handleAddBook}>
                            Submit
                        </Button>
                        <Button
                            variant="outlined"
                            color="secondary"
                            onClick={() => setShowAddForm(false)}
                            style={{ marginLeft: "10px" }}
                        >
                            Cancel
                        </Button>
                    </Box>
                </Box>
            ) : (
                <Grid container spacing={2}>
                    {books.map((book) => (
                        <Grid item xs={12} key={book.id}>
                            <Box border={1} borderRadius={2} p={2}>
                                <Typography variant="h6">{book.title}</Typography>
                                <Typography variant="body2">Author ID: {book.author_id}</Typography>
                                <Typography variant="body2">Year: {book.year}</Typography>
                                <Typography variant="body2">Category: {book.category}</Typography>
                                <Typography variant="body2">Price: ${book.pricing}</Typography>
                            </Box>
                        </Grid>
                    ))}
                </Grid>
            )}
        </Container>
    );
};

export default ManageBooks;
