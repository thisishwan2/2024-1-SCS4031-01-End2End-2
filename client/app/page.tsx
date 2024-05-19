'use client'
import { Box, Button, CssBaseline, Dialog, DialogActions, DialogTitle, TextField, Typography, useTheme } from "@mui/material";
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
import { StatusIcon } from "./[id]/page";
import Header from "./components/Header";



export default function Home() {
  const router = useRouter()
  const theme = useTheme();
  const [open, setOpen] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const queryClient = useQueryClient();
  const {data: scenarioList } = useQuery<{_id:string, scenario_name:string, run_status:string}[]>({queryKey: ['scenarios'], queryFn: async () => {
    const data = await fetch('http://127.0.0.1:5000/e2e/scenarios');
    return data.json();
  }, 
  refetchInterval: 10000

})

  const {mutate:postRunAll, isPending:isRunPending} = useMutation({mutationFn: async () => {
    return axios.post(`http://127.0.0.1:5000/e2e/scenarios/run-all`);
  },
  onSuccess:() => {
    queryClient.invalidateQueries({queryKey: ['scenarios']})
  }
},);



  const handleScenarioAdd = () => {
    setIsModalOpen(true);
  }

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  const handleScenarioRunAll = () => {
    postRunAll()
  }



  return (
    

    <>
    
    <Box sx={{ display: 'flex', height:"100%" }}>
      <CssBaseline />
      <Header/>
      <Box flexGrow={1} padding={theme.spacing(3)} paddingTop={theme.spacing(10)} >
        <Typography variant="h5" noWrap component="div">
            시나리오 목록
        </Typography>
        <Box display="flex" justifyContent="flex-end" padding="20px" gap="20px"> 
          <Button color="primary" variant="outlined" disabled={isRunPending} onClick={handleScenarioRunAll}>시나리오 전체 실행</Button>

          <Button color="primary" variant='contained' onClick={handleScenarioAdd}>시나리오 추가</Button>
        </Box>
        <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell align="center">시나리오 이름</TableCell>
            <TableCell align="center">상태</TableCell>
            <TableCell align="center">관리</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(scenarioList)?.map((scenario) => (
            <TableRow
              key={scenario._id}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              <TableCell align="center" component="th" scope="row">
                {scenario.scenario_name}
              </TableCell>
              <TableCell align="center"><StatusIcon status={scenario.run_status}/></TableCell>
              <TableCell align="center" >
                <Box display="flex" gap="20px" justifyContent="center">
                  <Button color="primary" variant="contained" onClick={() => {
                    router.push(`/${scenario._id}`)
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
    await axios.post("http://127.0.0.1:5000/e2e/scenarios",{scenario_name: name});
  }});
  const [name, setName] = useState("");
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
  }
  const handleAdd = () => {
    mutate(name,{
      onSuccess:() => {
        queryClient.invalidateQueries({queryKey: ['scenarios']})
        onClose();
      }
    })
  }
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xl" sx={{padding:"20px"}} >
      <DialogTitle>시나리오 추가</DialogTitle>
      <Box padding="20px" width="400px">
        <TextField label="시나리오 이름" fullWidth onChange={handleChange} value={name}/>
      </Box>
      <DialogActions>
        <Button disabled={!name} variant="contained" color="primary" onClick={handleAdd}>추가</Button>
        <Button variant="contained" color="error" onClick={onClose}>취소</Button>
      </DialogActions>
    </Dialog>
  )

}


// [
//   {id: "1", name: "로그인", run_status: "failed"},
//   {id: "2", name: "회원가입", run_status: "success"},
//   {id: "3", name: "탈퇴", run_status: "loading"},
//   {id: "4", name: "구매", run_status: "ready"},
// ]
// [
//   {
//     계층정보: "",
//     screenshot: "",
//     status:""
//   },
//   {
//     description:"",
//     status:"",
//   },
//   {
//     계층정보: "",
//     screenshot: "",
//     status:""
//   },
//   {
//     description:"",
//     status:"",
//   },
// ]