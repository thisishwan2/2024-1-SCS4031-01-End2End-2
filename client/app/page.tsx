'use client'
import { Box, Button, CssBaseline, Dialog, DialogActions, DialogTitle, InputLabel, MenuItem, Select, TextField, Typography, useTheme } from "@mui/material";
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
import SelectInput from "@mui/material/Select/SelectInput";



export default function Home() {
  const router = useRouter()
  const theme = useTheme();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isRunModalOpen, setIsRunModalOpen] = useState(false);
  const queryClient = useQueryClient();
  const {data: scenarioList } = useQuery<{_id:string, scenario_name:string, run_status:string}[]>({queryKey: ['scenarios'], queryFn: async () => {
    const data = await fetch('http://127.0.0.1:5000/e2e/scenarios');
    return data.json();
  }, 
  refetchInterval: 10000

})





  const handleScenarioAdd = () => {
    setIsModalOpen(true);
  }


  const handleScenarioRunAll = () => {
    setIsRunModalOpen(true)
  }



  return (
    

    <>
    
    <Box sx={{ display: 'flex', height:"100%" }}>

      <Box flexGrow={1} padding={theme.spacing(3)} paddingTop={theme.spacing(10)} >
        <Typography variant="h5" noWrap component="div">
            시나리오 목록
        </Typography>
        <Box display="flex" justifyContent="flex-end" padding="20px" gap="20px"> 
          <Button color="primary" variant="outlined" onClick={handleScenarioRunAll}>시나리오 전체 실행</Button>

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
    <RunDialog open={isRunModalOpen} onClose={() => setIsRunModalOpen(false)}/>
    </>
  );
}
interface DialogProps {
  open: boolean;
  onClose: () => void;
}

const AddDialog:React.FC<DialogProps> = ({open, onClose}) => {
  const queryClient= useQueryClient();

  const { mutate } = useMutation({"mutationFn": async ({name, templateId}:{name: string,templateId?:string}) => {
    await axios.post("http://127.0.0.1:5000/e2e/scenarios",{scenario_name: name, template_id:templateId});
  }});
  const {data: templateList } = useQuery<{_id:string, template_name:string, run_status:string}[]>({queryKey: ['templates'], queryFn: async () => {
    const data = await fetch('http://127.0.0.1:5000/e2e/templates');
    return data.json();
  }
  });
  const [name, setName] = useState("");
  const [template, setTemplate] = useState<string>();
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
  }
  const handleAdd = () => {
    mutate({name,templateId: template},{
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
      <Box padding="20px" width="400px">
        <InputLabel id="demo-simple-select-label">템플릿 불러오기</InputLabel>
      
        <Select labelId="demo-simple-select-label" label="템플릿 불러오기" fullWidth onChange={(e)=>{
          setTemplate(e.target.value);
        }} value={template}>
          {templateList?.map(template => (<MenuItem key={template._id} value={template._id}>{template.template_name}</MenuItem>))}
        </Select>
      </Box>
      <DialogActions>
        <Button disabled={!name} variant="contained" color="primary" onClick={handleAdd}>추가</Button>
        <Button variant="contained" color="error" onClick={onClose}>취소</Button>
      </DialogActions>
    </Dialog>
  )

}

const RunDialog:React.FC<DialogProps> = ({open, onClose}) => {
  const queryClient= useQueryClient();

  const {mutate:postRunAll, isPending:isRunPending} = useMutation({mutationFn: async (name:string) => {
    return axios.post(`http://127.0.0.1:5000/e2e/scenarios/run-all`,{report_name: name});
  },
  onSuccess:() => {
    queryClient.invalidateQueries({queryKey: ['scenarios']})
    onClose();
  }
},);
  const [name, setName] = useState("");
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
  }
  const handleRun = () => {
    postRunAll(name, {
      onSuccess:() => {
        queryClient.invalidateQueries({queryKey: ['scenarios']})
        onClose();
      }
    })
  }
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xl" sx={{padding:"20px"}} >
      <DialogTitle>리포트 이름 입력</DialogTitle>
      <Box padding="20px" width="400px">
        <TextField label="리포트 이름" placeholder="ex) 2024-05-18 통합 QA" fullWidth onChange={handleChange} value={name}/>
      </Box>
      <DialogActions>
        <Button disabled={!name} variant="contained" color="primary" onClick={handleRun}>전체 실행</Button>
        <Button variant="contained" color="error" onClick={onClose}>취소</Button>
      </DialogActions>
    </Dialog>
  )

}

