import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Typography, Button, Grid, TextField, Box, Paper } from "@mui/material";

const ManageAuthors = () => {
  const [authors, setAuthors] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newAuthor, setNewAuthor] = useState({
    first_name: "",
    last_name: "",
    date_of_birth: "",
    nationality: "",
  });

  // Fetch authors
  useEffect(() => {
    fetchAuthors();
  }, []);

  const fetchAuthors = async () => {
    try {
      const response = await axios.get("/authors");
      setAuthors(response.data);
    } catch (error) {
      console.error("Error fetching authors:", error);
    }
  };

  // Handle adding a new author
  const handleAddAuthor = async () => {
    try {
      const response = await axios.post("/authors", newAuthor);
      setAuthors([...authors, response.data]);
      setShowAddForm(false);
      setNewAuthor({ first_name: "", last_name: "", date_of_birth: "", nationality: "" });
    } catch (error) {
      console.error("Error adding author:", error);
    }
  };

  // Handle input change in the form
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewAuthor({ ...newAuthor, [name]: value });
  };

  // Handle cancel button to hide the form
  const handleCancel = () => {
    setShowAddForm(false);
    setNewAuthor({ first_name: "", last_name: "", date_of_birth: "", nationality: "" });
  };

  return (
    <Container maxWidth="md">
      {/* Title and Button Container */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4">Manage Authors</Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => setShowAddForm(true)}  // Show the Add Author form
        >
          + Add Author
        </Button>
      </Box>

      {/* Add Author Form */}
      {showAddForm ? (
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
            <Button variant="contained" color="success" onClick={handleAddAuthor} sx={{ marginRight: "10px" }}>
              Submit
            </Button>
            <Button variant="outlined" color="secondary" onClick={handleCancel}>
              Cancel
            </Button>
          </Box>
        </Box>
      ) : (
        // Author List
        <Grid container spacing={2}>
          {authors.map((author) => (
            <Grid item xs={12} key={author.id}>
              <Paper elevation={3} sx={{ padding: "16px", display: "flex", justifyContent: "space-between" }}>
                <div>
                  <Typography variant="h6">{author.first_name} {author.last_name}</Typography>
                  <Typography variant="body2">Date of Birth: {author.date_of_birth}</Typography>
                  <Typography variant="body2">Nationality: {author.nationality}</Typography>
                </div>
                {/* Add any other buttons you want to add */}
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default ManageAuthors;
