import React from "react";
import { Container, Typography } from "@mui/material";

const ChatWithLibrarian = () => {
    return (
        <Container maxWidth="md" style={{ textAlign: "center", marginTop: "2rem" }}>
            <Typography variant="h3" gutterBottom>
                Chat with Librarian
            </Typography>
            <Typography variant="body1" color="textSecondary">
                Welcome to the chat! How can we assist you today?
            </Typography>
        </Container>
    );
};

export default ChatWithLibrarian;
