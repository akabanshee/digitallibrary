import { createTheme } from "@mui/material/styles";

const theme = createTheme({
    palette: {
        primary: {
            main: "#3f51b5", // Mavi
        },
        secondary: {
            main: "#f50057", // Pembe
        },
    },
    typography: {
        h2: {
            fontFamily: "Roboto, sans-serif",
            fontWeight: 700,
        },
        h6: {
            fontFamily: "Roboto, sans-serif",
            fontWeight: 300,
        },
    },
});

export default theme;
