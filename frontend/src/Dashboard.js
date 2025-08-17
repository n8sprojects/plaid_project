import React, { useState } from "react";
import { usePlaidLink } from "react-plaid-link";
import { Button, Box, Typography } from "@mui/material";

export default function Dashboard({ username }) {
    
  const [linkToken, setLinkToken] = useState(null);
  const [message, setMessage] = useState("");

  const createLinkToken = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/create_link_token");
      const data = await res.json();
      setLinkToken(data.link_token);
    } catch (err) {
      console.error(err);
      setMessage("Failed to create link token");
    }
  };

  const onSuccess = async (public_token) => {
    try {
      const res = await fetch("http://127.0.0.1:5000/exchange_public_token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ public_token, username }),
      });
      const data = await res.json();
      setMessage(data.message || "Bank connected successfully!");
    } catch (err) {
      console.error(err);
      setMessage("Failed to connect bank");
    }
  };

  const config = {
    token: linkToken,
    onSuccess,
  };

  const { open, ready } = usePlaidLink(config);

  return (
    <Box maxWidth={600} mx="auto" mt={5} p={4} boxShadow={3} borderRadius={2}>
      <Typography variant="h5" mb={2}>Dashboard</Typography>
      <Typography mb={2}>Logged in as: {username}</Typography>

      <Button
        variant="contained"
        color="primary"
        onClick={linkToken ? open : createLinkToken}
        disabled={!ready && !!linkToken}
      >
        {linkToken ? "Connect Bank" : "Generate Link Token"}
      </Button>

      {message && (
        <Typography mt={2} color="error">
          {message}
        </Typography>
      )}
    </Box>
  );
}
