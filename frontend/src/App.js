import { useEffect, useState } from 'react';

function App() {
  const [linkToken, setLinkToken] = useState(null);

  const getLinkToken = async () => {
    const res = await fetch('http://localhost:5000/create_link_token'); // Flask endpoint
    const data = await res.json();
    setLinkToken(data.link_token);
  };

  useEffect(() => {
    getLinkToken();
  }, []);

  return (
    <div>
      <h1>Plaid Quickstart Test</h1>
      {linkToken ? (
        <p>Link Token: {linkToken}</p>
      ) : (
        <p>Loading Link Token...</p>
      )}
    </div>
  );
}

export default App;