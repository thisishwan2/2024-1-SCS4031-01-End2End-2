'use client'
import { AppBar, Box, Dialog, List, ListItem, ListItemButton, ListItemText, Toolbar, Typography } from "@mui/material"
import E2eSpaceIcon from '../e2e-space.svg';
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { StatusIcon } from "../[id]/page";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";


const Header = () => {
  const [isOpen, setIsOpen] = useState(false);
  const {isSuccess, isError,refetch, isLoading} = useQuery({queryKey: ['device-connection'], enabled:false, queryFn: async () => {
    const response =  await axios.get<{
      message: string;
    }>(`http://127.0.0.1:5000/e2e/device-connection`);
    return response.data;
  }
  });
  const path = usePathname();
  

  return (
    <>
    <AppBar color="inherit">
    <Toolbar>
      <E2eSpaceIcon />
      <List sx={{display:"flex",marginLeft:"30px" }}>
      {[{text: '시나리오 관리',href: "/"},{text: '템플릿 관리',href: "/templates"}].map(({text,href}, index) =>{
        return (
        <ListItem key={text} disablePadding sx={{whiteSpace:"nowrap"}}>
          <Box sx={{padding:"8px 16px"}}>
            <Link style={{textDecoration:"none", fontWeight:"bold"}}  href={href}>
              <ListItemText primary={text} sx={{ color: href === path ? "#1976d2" : "grey", ":hover": {color: href === path ? "#1976d2" :"black"}}}/>
            </Link>
          </Box>
        </ListItem>
      )})}
      <ListItem disablePadding sx={{whiteSpace:"nowrap"}}>
        <ListItemButton onClick={async ()=>{
          try {
            
            await refetch();
            setIsOpen(true);
            
          }catch(e) {
            setIsOpen(true);
          }
        }} sx={{display:"flex", alignItems:"center", gap:"5px"}}>
          <ListItemText primary={"디바이스 연결 확인"} />
          <StatusIcon status={isSuccess ? "success" : isError ? "fail": isLoading ? "loading" : "ready"} hasText={false}/>
        </ListItemButton>
      </ListItem>
    </List>

      
    </Toolbar>
  </AppBar>
  <Dialog open={isOpen} onClose={()=> {setIsOpen(false)}} maxWidth="xl" sx={{padding:"20px"}} >
      
      <Box padding="20px" width="400px">
        {isError ? <Typography textAlign="center" variant="h5">디바이스 연결되지 않음</Typography>: <Typography textAlign="center" variant="h5">디바이스 연결됨</Typography>}
      </Box>
    </Dialog>
  </>
  )
}

export default Header


