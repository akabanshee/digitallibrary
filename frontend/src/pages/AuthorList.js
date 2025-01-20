import React, { useEffect, useState } from "react";
import { Container, Typography, Button, Grid, Card, CardContent, TextField, Box } from "@mui/material";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const AuthorList = () => {
    const [authors, setAuthors] = useState([]);
    const [newAuthor, setNewAuthor] = useState({
        first_name: "",
        last_name: "",
        date_of_birth: "",
        nationality: "",
    });
    const [showAddForm, setShowAddForm] = useState(false);
    const navigate = useNavigate();
    const [filterFirstName, setFilterFirstName] = useState("");
    const [filterLastName, setFilterLastName] = useState("");
    const [filterNationality, setFilterNationality] = useState("");


    // Fetch authors from the backend
    useEffect(() => {
        axios.get("/authors")
            .then(response => setAuthors(response.data))
            .catch(error => console.error(error));
    }, []);

    // Handle form input changes
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewAuthor({ ...newAuthor, [name]: value });
    };

    // Handle form submission to add a new author
    const handleAddAuthor = async () => {
        try {
            const response = await axios.post("/authors", newAuthor);
            setAuthors([...authors, response.data]);
            setShowAddForm(false);
            setNewAuthor({
                first_name: "",
                last_name: "",
                date_of_birth: "",
                nationality: "",
            });
        } catch (error) {
            console.error("Error adding author:", error);
        }
    };

    // Handle "Go Back" button click to navigate back to Home Page
    const handleGoBack = () => {
        navigate("/");  // Navigate to the home page
    };

    // Handle deleting an author
    const handleDeleteAuthor = async (authorId) => {
        try {
            await axios.delete(`/authors/${authorId}`);
            setAuthors(authors.filter((author) => author.id !== authorId));
        } catch (error) {
            console.error("Error deleting author:", error);
        }
    };

    const handleFilterAuthors = () => {
        let filteredAuthors = authors;
    
        if (filterFirstName) {
            filteredAuthors = filteredAuthors.filter((author) =>
                author.first_name.toLowerCase().includes(filterFirstName.toLowerCase())
            );
        }
        if (filterLastName) {
            filteredAuthors = filteredAuthors.filter((author) =>
                author.last_name.toLowerCase().includes(filterLastName.toLowerCase())
            );
        }
        if (filterNationality) {
            filteredAuthors = filteredAuthors.filter((author) =>
                author.nationality.toLowerCase().includes(filterNationality.toLowerCase())
            );
        }
    
        setAuthors(filteredAuthors);
    };
    

    return (
        <Container maxWidth="md" style={{ marginTop: "2rem" }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" marginBottom="1rem">
                <Button
                    variant="contained"
                    color="secondary"
                    onClick={handleGoBack}  // Navigate to the home page when clicked
                    style={{ marginBottom: "1rem" }}
                >
                    Go Back
                </Button>
                <Button
                    variant="contained"
                    color="primary"
                    onClick={() => setShowAddForm(!showAddForm)}
                    style={{ marginBottom: "1rem" }}
                >
                    + Add Author
                </Button>
            </Box>

            <Typography variant="h4" gutterBottom>
                Author List
            </Typography>
            {/* Filtreleme Alanı */}
            <Box display="flex" alignItems="center" marginBottom={4} style={{ gap: "15px" }}>
                <TextField
                    label="Filter by First Name"
                    value={filterFirstName}
                    onChange={(e) => setFilterFirstName(e.target.value)}
                    style={{ marginRight: "10px" }}
                />
                <TextField
                    label="Filter by Last Name"
                    value={filterLastName}
                    onChange={(e) => setFilterLastName(e.target.value)}
                    style={{ marginRight: "10px" }}
                />
                <TextField
                    label="Filter by Nationality"
                    value={filterNationality}
                    onChange={(e) => setFilterNationality(e.target.value)}
                    style={{ marginRight: "10px" }}
                />
                <Button
                    variant="contained"
                    color="primary"
                    onClick={handleFilterAuthors}
                    style={{ marginRight: "10px" }}
                >
                Filter
            </Button>
            <Button
                variant="outlined"
                color="secondary"
                onClick={() => {
                    setFilterFirstName(""); // Filtreleri temizle
                    setFilterLastName("");
                    setFilterNationality("");
                axios
                    .get("/authors") // Yazarları yeniden getir
                    .then(response => setAuthors(response.data))
                    .catch(error => console.error(error));
                }}
            >
            Clear
            </Button>
            </Box>
            {/* Display the add author form */}
            {showAddForm && (
                <Box component="form" noValidate autoComplete="off" mb={4}>
                    <Typography variant="h6" mb={2}>Add a New Author</Typography>
                    <Grid container spacing={2}>
                        <Grid item xs={6}>
                            <TextField
                                fullWidth
                                label="First Name"
                                name="first_name"
                                value={newAuthor.first_name}
                                onChange={handleInputChange}
                                required
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                fullWidth
                                label="Last Name"
                                name="last_name"
                                value={newAuthor.last_name}
                                onChange={handleInputChange}
                                required
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                fullWidth
                                label="Date of Birth"
                                name="date_of_birth"
                                type="date"
                                InputLabelProps={{ shrink: true }}
                                value={newAuthor.date_of_birth}
                                onChange={handleInputChange}
                                required
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                fullWidth
                                label="Nationality"
                                name="nationality"
                                value={newAuthor.nationality}
                                onChange={handleInputChange}
                                required
                            />
                        </Grid>
                    </Grid>
                    <Box mt={2}>
                        <Button variant="contained" color="success" onClick={handleAddAuthor}>
                            Submit
                        </Button>
                        <Button variant="outlined" color="secondary" onClick={() => setShowAddForm(false)}>
                            Cancel
                        </Button>
                    </Box>
                </Box>
            )}

            <Grid container spacing={2}>
                {authors.map((author) => (
                    <Grid item xs={12} key={author.id}>
                        <Card>
                            <CardContent style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                <Box>
                                    <Typography
                                        variant="h6"
                                        style={{ cursor: "pointer", color: "blue", fontWeight: 'bold' }}
                                        onClick={() => navigate(`/author/${author.id}`)}  // Navigate to the author's detail page
                                    >
                                        {author.first_name} {author.last_name}
                                    </Typography>
                                    <Typography>Date of Birth: {author.date_of_birth}</Typography>
                                    <Typography>Nationality: {author.nationality}</Typography>
                                </Box>
                                <Button
                                    variant="contained"
                                    color="secondary"
                                    onClick={() => handleDeleteAuthor(author.id)}
                                    style={{ marginLeft: "10px" }}
                                >
                                    REMOVE
                                </Button>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Container>
    );
};

export default AuthorList;
