import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Typography, Grid, Button, TextField, Card, CardContent, Box, MenuItem } from "@mui/material";



const BookList = () => {
    const [books, setBooks] = useState([]);
    const [authors, setAuthors] = useState([]);
    const [showAddForm, setShowAddForm] = useState(false);
    const [showUpdateForm, setShowUpdateForm] = useState(false);
    const [loading, setLoading] = useState(false); 
    const [selectedBook, setSelectedBook] = useState(null);
    const [filterMinPrice, setFilterMinPrice] = useState("");
    const [filterMaxPrice, setFilterMaxPrice] = useState("");
    const [filterCategory, setFilterCategory] = useState("");
    const [filterYear, setFilterYear] = useState("");

    const [newBook, setNewBook] = useState({
        title: "",
        author_id: "",
        year: "",
        pricing: "",
        category: "",
        file: null,
    });



    useEffect(() => {
        fetchBooks();
        fetchAuthors();
    }, []);

    const fetchBooks = async () => {
        setLoading(true); // Yükleme başlıyor
        try {
            const response = await axios.get("/books");
            setBooks(response.data); // Tüm kitapları books state'ine kaydet
        } catch (error) {
            console.error("Error fetching books:", error);
        } finally {
            setLoading(false); // Yükleme bitiyor
        }
    };
    


    const handleFilter = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (filterYear) params.append("year", filterYear);
            if (filterMinPrice) params.append("min_price", filterMinPrice);
            if (filterMaxPrice) params.append("max_price", filterMaxPrice);
            if (filterCategory) params.append("category", filterCategory);
    
            const response = await axios.get(`/books?${params.toString()}`);
            setBooks(response.data);
        } catch (error) {
            console.error("Error filtering books:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleClearFilter = () => {
        setFilterYear("");
        setFilterMinPrice("");
        setFilterMaxPrice("");
        setFilterCategory("");
        fetchBooks();
    };
    



    

    const fetchAuthors = async () => {
        try {
            const response = await axios.get("/authors");
            setAuthors(response.data);
        } catch (error) {
            console.error("Error fetching authors:", error);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        const parsedValue = name === "author_id" ? parseInt(value) : value;
    
        if (showUpdateForm) {
            setSelectedBook({ ...selectedBook, [name]: parsedValue });
        } else {
            setNewBook({ ...newBook, [name]: parsedValue });
        }
    };
    

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file && file.size > 5 * 1024 * 1024) {
            alert("File size must be less than 5MB");
            return;
        }
        if (showUpdateForm) {
            setSelectedBook({ ...selectedBook, file });
        } else {
            setNewBook({ ...newBook, file });
        }
    };

    const handleAddBook = async () => {
        try {
            const formData = new FormData();
            formData.append("title", newBook.title);
            formData.append("author_id", parseInt(newBook.author_id));
            formData.append("year", parseInt(newBook.year));
            formData.append("pricing", parseFloat(newBook.pricing));
            formData.append("category", newBook.category);
            if (newBook.file) formData.append("pdf_file", newBook.file); // ✅ doğru field adı
    
            await axios.post("/books/", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
    
            fetchBooks();
            setShowAddForm(false);
            setNewBook({
                title: "",
                author_id: "",
                year: "",
                pricing: "",
                category: "",
                file: null,
            });
        } catch (error) {
            console.error("Error adding book:", error.response?.data || error.message);
            alert("Kitap eklenemedi: " + (error.response?.data?.detail || "Form verisi hatalı olabilir."));
        }
    };
    

    const handleUpdateBook = async () => {
        try {
            const formData = new FormData();
            formData.append("title", selectedBook.title);
            formData.append("author_id", parseInt(selectedBook.author_id));
            formData.append("year", parseInt(selectedBook.year));
            formData.append("pricing", parseFloat(selectedBook.pricing));
            formData.append("category", selectedBook.category);
            if (selectedBook.file) formData.append("file", selectedBook.file);

            await axios.put(`/books/${selectedBook.id}`, formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });

            fetchBooks();
            setShowUpdateForm(false);
            setSelectedBook(null);
        } catch (error) {
            console.error("Error updating book:", error.response?.data || error.message);
            alert("Failed to update book. Please check the inputs.");
        }
    };

    const handleDownloadPDF = async (bookId) => {
        try {
            const response = await axios.get(`/books/${bookId}/download`);
            const pdfUrl = response.data.download_link;
            window.open(pdfUrl, "_blank");
        } catch (error) {
            console.error("Error downloading PDF:", error.response?.data || error.message);
            alert("Failed to download the PDF.");
        }
    };

    const openUpdateForm = (book) => {
        setSelectedBook(book);
        setShowUpdateForm(true);
    };

    const handleRemoveBook = async (bookId) => {
        try {
            await axios.delete(`/books/${bookId}`);
            fetchBooks(); // Refresh the book list
        } catch (error) {
            console.error("Error removing book:", error);
            alert("Failed to remove book.");
        }
    };


    return (
        <Container>
            <Box display="flex" justifyContent="space-between" alignItems="center" marginBottom={2}>
                <Button
                    variant="contained"
                    color="secondary"
                    onClick={() => window.history.back()}
                >
                    GO BACK
                </Button>
                <Typography variant="h4" gutterBottom>
                    Book List
                </Typography>
                <Button
                    variant="contained"
                    color="primary"
                    onClick={() => setShowAddForm(!showAddForm)}
                >
                    {showAddForm ? "Cancel" : "ADD BOOK"}
                </Button>
            </Box>
            <Box
                display="flex"         // Esnek düzenleme için Flexbox'ı etkinleştir
                flexWrap="wrap"        // Alan daraldığında yeni satıra geç
                alignItems="center"    // Dikey hizalamayı ortala
                style={{ gap: "15px", justifyContent: "space-between" }} // Boşluk ve dağılım ayarı
            >
                <TextField
                    label="Filter by Year"
                    type="number"
                    value={filterYear}
                    onChange={(e) => setFilterYear(e.target.value)}
                    style={{ marginRight: "10px" }}
                />
                <TextField
                    label="Min Price"
                    type="number"
                    value={filterMinPrice}
                    onChange={(e) => setFilterMinPrice(e.target.value)}
                    style={{ marginRight: "10px" }}
                />
                <TextField
                    label="Max Price"
                    type="number"
                    value={filterMaxPrice}
                    onChange={(e) => setFilterMaxPrice(e.target.value)}
                    style={{ marginRight: "10px" }}
                />
                <TextField
  select
  label="Category"
  value={filterCategory}  // ✅ Doğru state
  onChange={(e) => setFilterCategory(e.target.value)}  // ✅ Doğru handler
  style={{ marginRight: "10px", width: "200px" }}
  fullWidth
>
  <MenuItem value="">Select Category</MenuItem>
  <MenuItem value="Bilim Kurgu">Science Fiction</MenuItem>
  <MenuItem value="Otobiyografi">Autobiography</MenuItem>
  <MenuItem value="Drama">Drama</MenuItem>
  <MenuItem value="Biyografi">Biography</MenuItem>
  <MenuItem value="Roman">Novel</MenuItem>
  <MenuItem value="Siir">Poem</MenuItem>
</TextField>



                <Button
                    variant="contained"
                    color="primary"
                    onClick={handleFilter}
                    style={{ marginRight: "10px" }}
                >
                    Filter
                </Button>
                <Button
                    variant="outlined"
                    color="secondary"
                    onClick={handleClearFilter}
                >
                    Clear
                </Button>
            </Box>
            {showAddForm && (
  <Card style={{ marginBottom: "20px" }}>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        Add New Book
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            label="Title"
            name="title"
            value={newBook.title}
            onChange={handleInputChange}
            fullWidth
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            select
            label="Author"
            name="author_id"
            value={newBook.author_id}
            onChange={handleInputChange}
            fullWidth
          >
            <MenuItem value="">Select Author</MenuItem>
            {authors.map((author) => (
              <MenuItem key={author.id} value={author.id}>
                {author.first_name} {author.last_name}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={6}>
          <TextField
            label="Year"
            name="year"
            type="number"
            value={newBook.year}
            onChange={handleInputChange}
            fullWidth
          />
        </Grid>
        <Grid item xs={6}>
          <TextField
            select
            label="Category"
            name="category"
            value={newBook.category}
            onChange={handleInputChange}
            fullWidth
          >
            <MenuItem value="">Select Category</MenuItem>
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
            label="Pricing"
            name="pricing"
            type="number"
            value={newBook.pricing}
            onChange={handleInputChange}
            fullWidth
          />
        </Grid>
        <Grid item xs={6}>
          <Button
            variant="contained"
            component="label"
            style={{ marginBottom: "10px" }}
          >
            Upload PDF
            <input
              type="file"
              hidden
              accept="application/pdf"
              onChange={handleFileChange}
            />
          </Button>
          {newBook.file && (
            <Typography variant="body2">
              Selected File: {newBook.file.name}
            </Typography>
          )}
        </Grid>
      </Grid>
      <Box mt={2}>
        <Button variant="contained" color="success" onClick={handleAddBook}>
          Submit
        </Button>
      </Box>
    </CardContent>
  </Card>
)}
            {showUpdateForm && (
                <Card style={{ marginBottom: "20px" }}>
                    <CardContent>
                        <Typography variant="h6" gutterBottom>
                            Update Book
                        </Typography>
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <TextField
                                    label="Title"
                                    name="title"
                                    value={selectedBook.title}
                                    onChange={handleInputChange}
                                    fullWidth
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    select
                                    label="Author"
                                    name="author_id"
                                    value={selectedBook.author_id}
                                    onChange={handleInputChange}
                                    fullWidth
                                >
                                    <MenuItem value="">Select Author</MenuItem>
                                    {authors.map((author) => (
                                        <MenuItem key={author.id} value={author.id}>
                                            {author.first_name} {author.last_name}
                                        </MenuItem>
                                    ))}
                                </TextField>
                            </Grid>
                            <Grid item xs={6}>
                                <TextField
                                    label="Year"
                                    name="year"
                                    type="number"
                                    value={selectedBook.year}
                                    onChange={handleInputChange}
                                    fullWidth
                                />
                            </Grid>
                            <Grid item xs={12} md={4}>
  <TextField
    select
    label="Category"
    name="category"
    value={selectedBook.category}
    onChange={handleInputChange}
    fullWidth
    InputProps={{
      style: { minWidth: "200px" },
    }}
  >
    <MenuItem value="">Select Category</MenuItem>
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
                                    label="Pricing"
                                    name="pricing"
                                    type="number"
                                    value={selectedBook.pricing}
                                    onChange={handleInputChange}
                                    fullWidth
                                />
                            </Grid>
                            <Grid item xs={6}>
                                <Button
                                    variant="contained"
                                    component="label"
                                    style={{ marginBottom: "10px" }}
                                >
                                    Upload PDF
                                    <input
                                        type="file"
                                        hidden
                                        accept="application/pdf"
                                        onChange={handleFileChange}
                                    />
                                </Button>
                                {selectedBook.file && (
                                    <Typography variant="body2">
                                        Selected File: {selectedBook.file.name}
                                    </Typography>
                                )}
                            </Grid>
                        </Grid>
                        <Box mt={2}>
                            <Button variant="contained" color="primary" onClick={handleUpdateBook}>
                                Update
                            </Button>
                            <Button
                                variant="outlined"
                                color="secondary"
                                onClick={() => {
                                    setShowUpdateForm(false);
                                    setSelectedBook(null);
                                }}
                                style={{ marginLeft: "10px" }}
                            >
                                Cancel
                            </Button>
                        </Box>
                    </CardContent>
                </Card>
            )}

            <Grid container spacing={2}>
                {books.map((book) => (
                    <Grid item xs={12} key={book.id}>
                        <Card>
                            <CardContent style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                <Box>
                                    <Typography variant="h6" style={{ fontWeight: 'bold', color: "#2C3E50" }}>{book.title}</Typography>
                                    <Typography style={{ color: "#34495E" }}>Author: {book.author}</Typography>
                                    <Typography style={{ color: "#7F8C8D" }}>Year: {book.year}</Typography>
                                    <Typography style={{ color: "#27AE60", fontWeight: 'bold' }}>Price: ₺{book.pricing}</Typography>
                                    <Typography style={{ color: "#3498DB", fontSize: "0.9em" }}>Category: {book.category}</Typography>
                                </Box>
                                <Box>
                                    <Button
                                        variant="contained"
                                        color="primary"
                                        style={{ marginRight: "10px", marginBottom: "10px" }}
                                        onClick={() => openUpdateForm(book)}
                                    >
                                        UPDATE
                                    </Button>
                                    <Button
                                        variant="contained"
                                        color="primary"
                                        style={{ marginRight: "10px", marginBottom: "10px" }}
                                        onClick={() => handleDownloadPDF(book.id)}
                                    >
                                        ACCESS PDF
                                    </Button>
                                    <Button
                                        variant="contained"
                                        color="secondary"
                                        style={{ marginBottom: "10px" }}
                                        onClick={() => handleRemoveBook(book.id)}
                                    >
                                        REMOVE
                                    </Button>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Container>
    );
};

export default BookList;
