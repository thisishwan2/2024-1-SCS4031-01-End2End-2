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
  const [isModalOpen, setIsModalOpen] = useState(false);
  const {data } = useQuery<{_id:string, report_name:string, created_at:string}[]>({queryKey: ['reports'], queryFn: async () => {
      const data = await fetch('http://127.0.0.1:5000/e2e/reports');
      return data.json();
    }, 
    refetchInterval: 10000
  });

  const reportList = data || [{_id:"1", report_name:"report1", created_at:"2021-10-10"},{_id:"2", report_name:"report2", created_at:"2021-10-11"}];




  const handleReportAdd = () => {
    setIsModalOpen(true);
  }
  return (
    

    <>
    
    <Box sx={{ display: 'flex', height:"100%" }}>
      <Box flexGrow={1} padding={theme.spacing(3)} >
        <DrawerHeader />
        <Typography variant="h5" noWrap component="div">
            테스트 리포트
        </Typography>
        <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell align="center">리포트 이름</TableCell>
            <TableCell align="center">테스트 실행일자</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(reportList)?.map((report) => (
            <TableRow
              key={report._id}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              hover
              onClick={() => {
                router.push(`/reports/${report._id}`);
              }}
            >
              <TableCell align="center" component="th" scope="row">
                {report.report_name}
              </TableCell>

              <TableCell align="center" >
                {report.created_at}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
    
      </Box>
    </Box>
    </>
  );
}
