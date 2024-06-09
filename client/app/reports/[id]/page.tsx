'use client'
import { Box, Button, CircularProgress, CssBaseline, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography, useTheme } from "@mui/material";

import { useEffect, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import axios from "axios";
import Image from "next/image";
import { BlockOutlined, CancelOutlined, CheckCircleOutline, CircleOutlined,  } from "@mui/icons-material";
import Guide from "@/app/components/Guide";

interface Report {
  _id: string;
  create_at: string;
  fail_report: FailReport[];
  fail_scenario_cnt: number;
  pass_fail_per: number;
  report_name: string;
  running_scenario_cnt: number;
  success_all_per: number;
  success_scenario_cnt: number;
}

interface FailReport {
  existing_action: string;
  existing_new_screen: string;
  existing_old_screen: string;
  fail_new_screen: string;
  scenario_name: string;
}

export default function Home() {
  const {id} = useParams();
  const {data} = useQuery({queryKey: ['reports', 'detail', id], queryFn: async ()=> {
      const response =  await axios.get<Report>(`http://127.0.0.1:5000/e2e/reports/${id}`);
      return response.data;
    },  
  });
  // default mock data
  const reportDetail = data || { 
    _id: "1",
    create_at: "2021-10-10",
    fail_report: [
      {
        existing_action: "action1",
        existing_new_screen: "new_screen1",
        existing_old_screen: "old_screen1",
        fail_new_screen: "fail_new_screen1",
        scenario_name: "scenario1"
      }
    ],
    fail_scenario_cnt: 1,
    pass_fail_per: 0,
    report_name: "report1",
    running_scenario_cnt: 1,
    success_all_per: 0,
    success_scenario_cnt: 0
  };
  


  const theme = useTheme();


  return (
    <Box sx={{ display: 'flex', flexDirection:"column" }}>
      
      <Box flexGrow={1} padding={theme.spacing(3)} paddingTop={theme.spacing(10)} >

              <>
              <Box  display="flex" gap="20px" alignItems="center" marginBottom="15px">
                <Typography variant="h5" margin="0">
                  {reportDetail?.report_name}
                </Typography>

              </Box>
                <Typography variant="h6" margin="0">
                  테스트 요약
                </Typography>
                
                <Table>
                  {/* 테스트 성공률, 실행된 시나리오 수, 통과한 시나리오 수, 실패한 시나리오 수 */}
                  <TableHead>
                  <TableRow>
                    <TableCell>테스트 성공률</TableCell>
                    <TableCell>실행된 시나리오 수</TableCell>
                    <TableCell>통과한 시나리오 수</TableCell>
                    <TableCell>실패한 시나리오 수</TableCell>
                  </TableRow>
                  </TableHead>
                  <TableBody>
                  <TableRow>
                    <TableCell>
                    {reportDetail?.success_all_per}%
                    </TableCell>
                    <TableCell>
                    {reportDetail?.running_scenario_cnt}
                    </TableCell>
                    <TableCell>
                    {reportDetail?.success_scenario_cnt}
                    </TableCell>
                    <TableCell>
                    {reportDetail?.fail_scenario_cnt}
                    </TableCell>
                  </TableRow>
                  </TableBody>
                </Table>
              <Box display="flex" gap="40px" alignItems="center" marginBottom="40px">

            </Box>
          </>
      </Box>
      <Guide/>
    </Box>
  );
}

const ActionBox = ({onClick, action, status}: {onClick:(action:string) => void; action?:string;status?:string}) => {

  const [actionText, setActionText] = useState('');
  const handleClick = () => {
    onClick(actionText);
  }
  return (<Box bgcolor="white" width="200px" height="300px" border="1px solid lightgrey" borderRadius="10px" padding="5px">
    <Box display="flex"  borderBottom="1px solid lightgrey" marginBottom="30px">

    <StatusIcon status={status} />
    <Typography marginLeft="35px" variant="h6">액션 정보</Typography>
    </Box>
    <TextField  label="액션정보" value={actionText|| action} onChange={(e)=> {
     setActionText(e.target.value);
    }} />
    <Box display="flex" justifyContent="center" marginTop="10px">

      <Button variant="contained" disabled={actionText ==="" || actionText===action} onClick={handleClick}>등록</Button>
    </Box>
</Box>)
}


export const StatusIcon = ({status}: {status?:string}) => {
  const Icon = ()=> {
    if(status ==="success"){
      return <CheckCircleOutline color="success" />
    }else if (status ==="fail"){
      return <CancelOutlined color="error" />
    } else if (status ==="loading"){
      return <Loading />
    } else if(status ==="cancel") {
      return <BlockOutlined color="disabled" />
    }
    
    return <CircleOutlined color="disabled" />
  }

  return <Box display="inline-flex" alignItems="center" >
    <Icon />
  </Box>
}

const Loading = () => {
  return (
      <CircularProgress color="info" size={20} />
  );
};
