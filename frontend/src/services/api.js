import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000"; // Backend'in base URL'i

export const fetchBooks = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/books/`);
        return response.data;
    } catch (error) {
        console.error("Error fetching books:", error);
        throw error;
    }
};
