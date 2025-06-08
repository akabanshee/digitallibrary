import React, { useState, useRef, useEffect } from "react";
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
import { marked } from "marked";
import dayjs from "dayjs";


const ChatWithLibrarian = () => {
  const [userInput, setUserInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    {
      sender: "ai",
      message: "Hello! I am your library assistant. How can I help you today?",
      timestamp: dayjs().format("HH:mm"),
    },
  ]);
  
  const chatEndRef = useRef(null); // 👀 Otomatik scroll için referans

  // 👇 Scroll fonksiyonu
  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // 👇 Her mesajdan sonra scroll
  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  const handleSendMessage = async () => {
    if (!userInput.trim()) return;
  
    const currentInput = userInput;
    const now = dayjs().format("HH:mm"); // 🕒
  
    setUserInput("");
    setChatHistory((prev) => [
      ...prev,
      { sender: "user", message: currentInput, timestamp: now },
    ]);
    setLoading(true);
  
    try {
      const response = await axios.post("http://127.0.0.1:8000/process", {
        user_input: currentInput,
      });
  
      const { status, type, data, message } = response.data;
      let aiMessage;
  
      if (status === "success") {
        aiMessage = marked(data);
      } else {
        aiMessage = `❌ ${message || "An error occurred."}`;
      }
  
      setChatHistory((prev) => [
        ...prev,
        { sender: "ai", message: aiMessage, timestamp: dayjs().format("HH:mm") },
      ]);
    } catch (error) {
      console.error("🚨 API Error:", error);
      setChatHistory((prev) => [
        ...prev,
        {
          sender: "ai",
          message: "❌ An error occurred while processing your request.",
          timestamp: dayjs().format("HH:mm"),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };
  

  return (
    <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column", bgcolor: "#f5f5f5" }}>
      <Box sx={{ py: 2, px: 3, display: "flex", alignItems: "center", backgroundColor: "white", boxShadow: 1 }}>
        <IconButton component={Link} to="/" sx={{ color: "primary.main", border: "1px solid", borderColor: "primary.main", mr: 2 }}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h5" fontWeight="bold" sx={{ flex: 1, textAlign: "center" }}>
          AI-Powered Library Assistant
        </Typography>
      </Box>
      <Container maxWidth="md" sx={{ py: 4, flex: 1, display: "flex", flexDirection: "column", gap: 3 }}>
        <Paper elevation={3} sx={{ p: 3, height: "60vh", overflowY: "auto", bgcolor: "#ffffff", borderRadius: "16px", boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)" }}>
          {chatHistory.map((msg, index) => (
            <Box key={index} sx={{ textAlign: msg.sender === "ai" ? "left" : "right", my: 1 }}>
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
                <Typography sx={{ fontSize: "16px", fontFamily: "Arial, sans-serif" }}>
                  {msg.sender === "ai" ? (
                    <span dangerouslySetInnerHTML={{ __html: msg.message }} />
                  ) : (
                    msg.message
                  )}
                </Typography>
                {/* 🕒 İşte zaman damgası burada! */}
      <Typography
        variant="caption"
        sx={{ display: "block", mt: 1, color: "gray", fontSize: "12px" }}
      >
        {msg.timestamp}
      </Typography>
              </Box>
            </Box>
          ))}
          <div ref={chatEndRef} /> {/* 👇 Scroll noktası */}
        </Paper>
        <Paper elevation={3} sx={{ p: 3, display: "flex", gap: 2, borderRadius: "12px", boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)" }}>
          <TextField 
            label="Type your question here..." 
            variant="outlined" 
            fullWidth 
            multiline
            minRows={1}
            maxRows={4}
            value={userInput} 
            onChange={(e) => setUserInput(e.target.value)} 
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            sx={{ borderRadius: "8px" }} 
          />
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleSendMessage} 
            disabled={loading} 
            sx={{ whiteSpace: "nowrap", borderRadius: "8px", fontWeight: "bold" }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : "Send"}
          </Button>
        </Paper>
      </Container>
    </Box>
  );
};

export default ChatWithLibrarian;
