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
    { sender: "ai", message: <Typography>Hello! I am your library assistant. How can I help you today?</Typography> },
  ]);
  const handleSendMessage = async () => {
    if (!userInput.trim()) return;
  
    setChatHistory((prev) => [...prev, { sender: "user", message: <Typography>{userInput}</Typography> }]);
    setLoading(true);
  
    try {
      const response = await axios.post("http://127.0.0.1:8000/process", {
        user_input: userInput,
      });
  
      console.log("📡 API Full Response:", response.data);
  
      const { status, type, data, message } = response.data;
      let aiMessage;
  
      if (status === "success") {
        if (type === "SQL") {
          if (Array.isArray(data) && data.length > 0) {
            if (data.length === 1 && Object.keys(data[0]).length === 1) {
              const countValue = Object.values(data[0])[0]; 
              aiMessage = <Typography>📊 The result is: <strong>{countValue}</strong></Typography>;
            } else {
              aiMessage = (
                <Box sx={{ p: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                    📚 Here are the relevant books:
                  </Typography>
                  {data.map((item, index) => (
                    <Typography key={index}>
                      📖 <strong>{item.title || "Unknown"}</strong> - {item.author || "Unknown"} ({item.year || "Unknown"})  
                      {item.file_path && (
                        <>
                          {" "}
                          | <a href={item.file_path} target="_blank" rel="noopener noreferrer">📂 Download PDF</a>
                        </>
                      )}
                    </Typography>
                  ))}
                </Box>
              );
            }
          }
        } else {
          aiMessage = <Typography>{String(data)}</Typography>;
        }
      } else {
        aiMessage = <Typography>❌ {message || "An error occurred."}</Typography>;
      }
  
      // **📌 Cevap verdikten sonra ekstra mesaj ekle**
      setChatHistory((prev) => [
        ...prev,
        { sender: "ai", message: aiMessage },
        { sender: "ai", message: <Typography>🤖 How can I help you more?</Typography> }, // **Ekstra mesaj burada!**
      ]);
  
    } catch (error) {
      console.error("🚨 API Error:", error);
    } finally {
      setUserInput("");
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
              <Box sx={{ 
                display: "inline-block", 
                bgcolor: msg.sender === "ai" ? "#e3f2fd" : "#c8e6c9", 
                p: 2, 
                borderRadius: "12px", 
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)", 
                maxWidth: "75%" 
              }}>
                {msg.message}
              </Box>
            </Box>
          ))}
        </Paper>
        <Paper elevation={3} sx={{ p: 3, display: "flex", gap: 2, borderRadius: "12px", boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)" }}>
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
