'use client'
import { Box, Button, Dialog, DialogActions, DialogTitle, TextField, Typography, styled, useTheme } from "@mui/material";
import {  useState } from "react";

import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import axios from "axios";

import Header from "../components/Header";


const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

export default function Home() {
  const router = useRouter()
  const theme = useTheme();
  const [open, setOpen] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const {data: templateList } = useQuery<{_id:string, template_name:string, run_status:string}[]>({queryKey: ['templates'], queryFn: async () => {
      const data = await fetch('http://127.0.0.1:5000/e2e/templates');
      return data.json();
    }, 
    refetchInterval: 10000
  });




  const handleTemplateAdd = () => {
    setIsModalOpen(true);
  }

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };



  return (
    

    <>
    
    <Box sx={{ display: 'flex', height:"100%" }}>
      <Header />
      <Box flexGrow={1} padding={theme.spacing(3)} >
        <DrawerHeader />
        <Typography variant="h5" noWrap component="div">
            QA 템플릿
        </Typography>
        <Box display="flex" justifyContent="flex-end" padding="20px" gap="20px">           
          <Button color="primary" variant='contained' onClick={handleTemplateAdd}>템플릿 추가</Button>
        </Box>
        <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell align="center">템플릿 이름</TableCell>
            <TableCell align="center">관리</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(templateList)?.map((template) => (
            <TableRow
              key={template._id}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              <TableCell align="center" component="th" scope="row">
                {template.template_name}
              </TableCell>

              <TableCell align="center" >
                <Box display="flex" gap="20px" justifyContent="center">
                  <Button color="primary" variant="contained" onClick={() => {
                    router.push(`/templates/${template._id}`)
                  }}>수정</Button>
                  <Button color="error" variant="contained">삭제</Button>
                </Box>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
    
      </Box>
    </Box>
    <AddDialog open={isModalOpen} onClose={() => {setIsModalOpen(false)}}/>
    </>
  );
}
interface DialogProps {
  open: boolean;
  onClose: () => void;
}

const AddDialog:React.FC<DialogProps> = ({open, onClose}) => {
  const queryClient= useQueryClient();

  const { mutate } = useMutation({"mutationFn": async (name: string) => {
    await axios.post("http://127.0.0.1:5000/e2e/templates",{template_name: name});
  }});
  const [name, setName] = useState("");
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
  }
  const handleAdd = () => {
    mutate(name,{
      onSuccess:() => {
        queryClient.invalidateQueries({queryKey: ['templates']})
        onClose();
      }
    })
  }
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xl" sx={{padding:"20px"}} >
      <DialogTitle>템플릿 추가</DialogTitle>
      <Box padding="20px" width="400px">
        <TextField label="템플릿 이름" fullWidth onChange={handleChange} value={name}/>
      </Box>
      <DialogActions>
        <Button disabled={!name} variant="contained" color="primary" onClick={handleAdd}>추가</Button>
        <Button variant="contained" color="error" onClick={onClose}>취소</Button>
      </DialogActions>
    </Dialog>
  )

}

