import { useState } from "react";
import { invoke } from "@tauri-apps/api/tauri";
import {  Grid } from "@mui/material";



function App() {
  const [greetMsg, setGreetMsg] = useState("");
  const [name, setName] = useState("");

  async function greet() {
    // Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
    setGreetMsg(await invoke("greet", { name }));
  }

  return (
    <Grid container columns={16}>
      <Grid item xs={4}>a</Grid>
      <Grid item xs={8}>b</Grid>
    </Grid>
  );
}

export default App;
