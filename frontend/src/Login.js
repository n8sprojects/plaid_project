import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom"; 
import { TextField, Button, Box, Typography } from "@mui/material";

export default function Login({ onLoginSuccess }) {
  const { register, handleSubmit } = useForm();
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    const res = await fetch("http://127.0.0.1:5000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const result = await res.json();

    if (result.success) {
      onLoginSuccess(data.username);
      setErrorMessage("");
      navigate("/dashboard", { state: { username: data.username } }); 
    } else {
      setErrorMessage(result.error);
    }
  };

  return (
    <Box maxWidth={400} mx="auto" mt={5} p={4} boxShadow={3} borderRadius={2}>
      <Typography variant="h5" mb={2}>Login</Typography>

      <form onSubmit={handleSubmit(onSubmit)}>
        <TextField label="Username" fullWidth {...register("username")} margin="normal" />
        <TextField label="Password" type="password" fullWidth {...register("password")} margin="normal" />

        {errorMessage && (
          <Typography color="error" mt={1} mb={1}>{errorMessage}</Typography>
        )}

        <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
          Login
        </Button>
      </form>
    </Box>
  );
}
