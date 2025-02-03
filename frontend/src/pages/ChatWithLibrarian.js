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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import { ArrowBack } from "@mui/icons-material";
import { Link } from "react-router-dom";
import axios from "axios";

const ChatWithLibrarian = () => {
  const [userInput, setUserInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatResponse, setChatResponse] = useState("");
  const [tableData, setTableData] = useState([]);

  const handleSendMessage = async () => {
    if (!userInput.trim()) return;
    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/process", {
        user_input: userInput,
      });
      const data = response.data;
      console.log("📡 API Response:", data);

      if (Array.isArray(data.response)) {
        setTableData(data.response);
        setChatResponse("");
      } else {
        setChatResponse(data.response);
        setTableData([]);
      }
    } catch (error) {
      console.error("🚨 API Error:", error);
      setChatResponse("An error occurred while contacting the server.");
      setTableData([]);
    } finally {
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
      {/* Üst Kısım */}
      <Box
        sx={{
          py: 2,
          px: 2,
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
        {/* Başlık Ortalanıyor */}
        <Box sx={{ flex: 1, display: "flex", justifyContent: "center" }}>
          <Typography variant="h5" fontWeight="bold">
            Welcome to AI-Powered Database Chat
          </Typography>
        </Box>
      </Box>

      {/* Ana İçerik */}
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
        {/* Soru Sorma Alanı */}
        <Paper elevation={1} sx={{ p: 3, backgroundColor: "#ffffff", textAlign: "center" }}>
          <Typography variant="body1" color="textSecondary" gutterBottom>
            Ask something about the database, and the AI will generate a query and get results for you!
          </Typography>

          <Box sx={{ display: "flex", gap: 2, mt: 2 }}>
            <TextField
              label="Ask about the database..."
              variant="outlined"
              fullWidth
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleSendMessage}
              disabled={loading}
              sx={{ whiteSpace: "nowrap" }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : "Ask AI"}
            </Button>
          </Box>
        </Paper>

        {/* Metinsel Yanıt */}
        {chatResponse && (
          <Paper elevation={1} sx={{ p: 3, backgroundColor: "#ffffff" }}>
            <Typography variant="h6" color="primary" gutterBottom>
              AI Response:
            </Typography>
            <Typography
              variant="body1"
              sx={{
                whiteSpace: "pre-wrap",
                fontFamily: "monospace",
              }}
            >
              {chatResponse}
            </Typography>
          </Paper>
        )}

        {/* Tablo Yanıtı */}
        {tableData.length > 0 && (
          <TableContainer component={Paper} elevation={1} sx={{ p: 2, overflowX: "auto" }}>
            <Table>
              <TableHead>
                <TableRow>
                  {Object.keys(tableData[0]).map((key) => (
                    <TableCell key={key}>
                      <strong>{key}</strong>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {tableData.map((row, index) => (
                  <TableRow key={index}>
                    {Object.entries(row).map(([key, value]) => (
                      <TableCell key={key}>
                        {key === "file_path" && value ? (
                          <a
                            href={value}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              color: "#1976d2",
                              textDecoration: "none",
                            }}
                          >
                            Open File
                          </a>
                        ) : (
                          String(value)
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Container>
    </Box>
  );
};

export default ChatWithLibrarian;
