import React, { useState } from "react";
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Paper,
  CircularProgress,
  IconButton,
} from "@mui/material";
import { ArrowBack } from "@mui/icons-material";
import { Link } from "react-router-dom";
import axios from "axios";

const ChatWithLibrarian = () => {
  const [userInput, setUserInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    { sender: "ai", message: "Hello! I am your library assistant. How can I help you today?" },
  ]);

  const handleSendMessage = async () => {
    if (!userInput.trim()) return;

    const newUserMessage = { sender: "user", message: userInput };
    setChatHistory((prev) => [...prev, newUserMessage]);
    setLoading(true);

    try {
      const response = await axios.post("http://127.0.0.1:8000/process", {
        user_input: userInput,
      });

      const data = response.data;
      console.log("📡 API Response:", data);

      let aiMessage = "";

      if (Array.isArray(data.response) && data.response.length > 0) {
        // Eğer bir liste döndürülmesi gerekiyorsa
        if (data.response[0].title) {
          aiMessage = (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Here are the books related to your query:
              </Typography>
              {data.response.map((item, index) => (
                <Box
                  key={index}
                  sx={{
                    mt: 2,
                    p: 2,
                    border: "1px solid #ddd",
                    borderRadius: "8px",
                    backgroundColor: "#f9f9f9",
                  }}
                >
                  <Typography><strong>Title:</strong> {item.title || "Unknown"}</Typography>
                  <Typography><strong>Author:</strong> {item.author || "Unknown"}</Typography>
                  <Typography><strong>Year:</strong> {item.year || "Unknown"}</Typography>
                  <Typography><strong>Category:</strong> {item.category || "Unknown"}</Typography>
                  <Typography><strong>Price:</strong> ${item.pricing?.toFixed(2) || "Unknown"}</Typography>
                </Box>
              ))}
            </Box>
          );
        } else {
          // Eğer sonuç bir sayıysa (örneğin COUNT gibi)
          const numericKey = Object.keys(data.response[0]).find((key) => typeof data.response[0][key] === "number");
          aiMessage = `There are ${data.response[0][numericKey]} ${userInput.includes("book") ? "books" : "items"} related to your query.`;
        }
        setChatHistory((prev) => [
          ...prev,
          { sender: "ai", message: aiMessage },
          { sender: "ai", message: "Can I assist you with anything else?" },
        ]);
      } else if (Array.isArray(data.response) && data.response.length === 0) {
        aiMessage = "Sorry, I couldn't find any information matching your query.";
        setChatHistory((prev) => [
          ...prev,
          { sender: "ai", message: aiMessage },
          { sender: "ai", message: "Can I assist you with anything else?" },
        ]);
      } else {
        aiMessage = data.response || "Sorry, I couldn't understand your request.";
        setChatHistory((prev) => [...prev, { sender: "ai", message: aiMessage }]);
      }
    } catch (error) {
      console.error("🚨 API Error:", error);
      setChatHistory((prev) => [
        ...prev,
        { sender: "ai", message: "Sorry, an error occurred while processing your request." },
      ]);
    } finally {
      setUserInput("");
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        bgcolor: "#f5f5f5",
      }}
    >
      {/* Header Section */}
      <Box
        sx={{
          py: 2,
          px: 3,
          display: "flex",
          alignItems: "center",
          backgroundColor: "white",
          boxShadow: 1,
        }}
      >
        <IconButton
          component={Link}
          to="/"
          sx={{
            color: "primary.main",
            border: "1px solid",
            borderColor: "primary.main",
            mr: 2,
          }}
        >
          <ArrowBack />
        </IconButton>
        <Typography variant="h5" fontWeight="bold" sx={{ flex: 1, textAlign: "center" }}>
          AI-Powered Library Assistant
        </Typography>
      </Box>

      {/* Main Content */}
      <Container
        maxWidth="md"
        sx={{
          py: 4,
          flex: 1,
          display: "flex",
          flexDirection: "column",
          gap: 3,
        }}
      >
        {/* Chat Section */}
        <Paper
          elevation={3}
          sx={{
            p: 3,
            height: "60vh",
            overflowY: "auto",
            bgcolor: "#ffffff",
            borderRadius: "16px",
            boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
          }}
        >
          {chatHistory.map((msg, index) => (
            <Box
              key={index}
              sx={{
                textAlign: msg.sender === "ai" ? "left" : "right",
                my: 1,
              }}
            >
              <Box
                sx={{
                  display: "inline-block",
                  bgcolor: msg.sender === "ai" ? "#e3f2fd" : "#c8e6c9",
                  p: 2,
                  borderRadius: "12px",
                  boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
                  maxWidth: "75%",
                }}
              >
                {typeof msg.message === "string" ? (
                  <Typography
                    sx={{
                      whiteSpace: "pre-wrap",
                      fontFamily: "Roboto, sans-serif",
                    }}
                  >
                    {msg.message}
                  </Typography>
                ) : (
                  msg.message
                )}
              </Box>
            </Box>
          ))}
        </Paper>

        {/* Input Section */}
        <Paper
          elevation={3}
          sx={{
            p: 3,
            display: "flex",
            gap: 2,
            borderRadius: "12px",
            boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
          }}
        >
          <TextField
            label="Type your question here..."
            variant="outlined"
            fullWidth
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
            sx={{ borderRadius: "8px" }}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSendMessage}
            disabled={loading}
            sx={{
              whiteSpace: "nowrap",
              borderRadius: "8px",
              fontWeight: "bold",
            }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : "Send"}
          </Button>
        </Paper>
      </Container>
    </Box>
  );
};

export default ChatWithLibrarian;
