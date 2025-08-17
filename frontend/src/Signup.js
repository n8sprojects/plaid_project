import React from "react";
import { useForm } from "react-hook-form";
import { TextField, Button, Box, Typography } from "@mui/material";

export default function Signup() {
  const { register, handleSubmit } = useForm();

  const onSubmit = async (data) => {
    const res = await fetch("http://127.0.0.1:5000/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const result = await res.json();
    alert(result.message || result.error);
  };

  return (
    <Box maxWidth={400} mx="auto" mt={5} p={4} boxShadow={3} borderRadius={2}>
      <Typography variant="h5" mb={2}>Signup</Typography>
      <form onSubmit={handleSubmit(onSubmit)}>
        <TextField label="Username" fullWidth {...register("username")} margin="normal" />
        <TextField label="Password" type="password" fullWidth {...register("password")} margin="normal" />
        <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
          Signup
        </Button>
      </form>
    </Box>
  );
}
