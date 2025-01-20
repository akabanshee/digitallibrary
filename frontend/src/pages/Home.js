import React from "react";
import { Container, Typography, Button, Grid } from "@mui/material";
import { useNavigate } from "react-router-dom";
import libraryImage from "../assets/capa_biblioteca_digital.png"; // Doğru görsel yolu

const Home = () => {
    const navigate = useNavigate();

    const handleViewBooks = () => {
        navigate("/books");
    };

    const handleExploreAuthors = () => {
        navigate("/authors"); // Yazarlar sayfasına yönlendirme
    };

    return (
        <Container maxWidth="md" style={{ textAlign: "center", marginTop: "2rem" }}>
            <img
                src={libraryImage}
                alt="Library"
                style={{ width: "45%", borderRadius: "10px", marginBottom: "1rem" }}
            />
            <Typography variant="h2" gutterBottom>
                Digital Library
            </Typography>
            <Typography variant="h6" color="textSecondary" paragraph>
                Discover your next favorite book in our extensive library collection. Browse by category, author, or price.
            </Typography>
            <Grid container justifyContent="center" spacing={2} style={{ marginTop: "2rem" }}>
                <Grid item>
                    <Button
                        variant="contained"
                        color="primary"
                        size="large"
                        onClick={handleViewBooks}
                    >
                        Manage Books
                    </Button>
                </Grid>
                <Grid item>
                    <Button
                        variant="contained"
                        color="secondary"
                        size="large"
                        onClick={handleExploreAuthors} // Bu fonksiyonu doğru şekilde ekliyoruz
                    >
                        Manage Authors
                    </Button>
                </Grid>
            </Grid>
        </Container>
    );
};

export default Home;
