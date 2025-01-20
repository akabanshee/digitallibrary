import React, { useEffect, useState } from "react";
import { Container, Typography, Grid, Card, CardContent, Box, Divider, Button } from "@mui/material";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";  // Import useParams and useNavigate hooks

const AuthorDetail = () => {
    const { authorId } = useParams();  // Get the author ID from the URL
    const [author, setAuthor] = useState(null);
    const [books, setBooks] = useState([]);
    const navigate = useNavigate();  // Initialize navigate hook

    // Fetch author details and books
    useEffect(() => {
        // Fetch author details
        axios.get(`/authors/${authorId}`)
            .then(response => setAuthor(response.data))
            .catch(error => console.error("Error fetching author:", error));

        // Fetch books by the author
        axios.get(`/books/by-author/${authorId}`)
            .then(response => setBooks(response.data))
            .catch(error => console.error("Error fetching books:", error));
    }, [authorId]);

    if (!author) return <Typography variant="h6">Loading...</Typography>;

    return (
        <Container maxWidth="md" style={{ marginTop: "2rem", paddingBottom: "2rem" }}>
            {/* Back Button */}
            <Box display="flex" justifyContent="flex-start" marginBottom="2rem">
                <Button
                    variant="outlined"
                    color="secondary"
                    onClick={() => navigate("/authors")} // Go back to the author list page
                >
                    Go Back
                </Button>
            </Box>

            {/* Title */}
            <Typography variant="h4" gutterBottom align="center" style={{ fontWeight: "bold", marginBottom: "1rem" }}>
                Author Details
            </Typography>

            {/* Author Info Card */}
            <Card style={{ marginBottom: "2rem", boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)" }}>
                <CardContent>
                    <Typography variant="h5" style={{ fontWeight: "bold" }}>
                        {author.first_name} {author.last_name}
                    </Typography>
                    <Typography variant="body1" color="textSecondary">
                        <strong>Date of Birth:</strong> {author.date_of_birth}
                    </Typography>
                    <Typography variant="body1" color="textSecondary">
                        <strong>Nationality:</strong> {author.nationality}
                    </Typography>
                </CardContent>
            </Card>

            {/* Divider */}
            <Divider style={{ marginBottom: "2rem" }} />

            {/* Books by Author */}
            <Typography variant="h5" gutterBottom style={{ fontWeight: "bold", marginBottom: "1rem" }}>
                Books by {author.first_name} {author.last_name}
            </Typography>

            <Grid container spacing={2}>
                {books.map((book) => (
                    <Grid item xs={12} sm={6} md={4} key={book.id}>
                        <Card style={{ boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)", borderRadius: "8px" }}>
                            <CardContent>
                                <Typography variant="h6" style={{ fontWeight: "bold", marginBottom: "0.5rem" }}>
                                    {book.title}
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                    <strong>Year:</strong> {book.year}
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                    <strong>Category:</strong> {book.category}
                                </Typography>
                                <Typography variant="body2" color="textSecondary">
                                    <strong>Price:</strong> ${book.pricing}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Container>
    );
};

export default AuthorDetail;
