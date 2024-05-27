'use client'
import { Box, Button, CircularProgress, CssBaseline, TextField, Typography, useTheme } from "@mui/material";

import { useEffect, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import axios from "axios";
import Image from "next/image";
import { BlockOutlined, CancelOutlined, CheckCircleOutline, CircleOutlined,  } from "@mui/icons-material";
import Guide from "@/app/components/Guide";



export default function Home() {
  const {id} = useParams();
  const router= useRouter();
  const queryClient= useQueryClient();
  const [shouldPolling, setShouldPolling] = useState(false);
  const {data: templateDetail} = useQuery({queryKey: ['templates', 'detail', id], queryFn: async ()=> {
      const response =  await axios.get<{
          _id: string;
          run_status: string;
          template_name: string;
          template: {screenshot_url?:string; ui_data?: string; status?:string; action?:string}[]
      }>(`http://127.0.0.1:5000/e2e/templates/${id}`);
      return response.data;
    },  
    refetchInterval: shouldPolling ? 1000 : undefined
  })

  useEffect(() => {
    if(templateDetail) {
      if(templateDetail.run_status === "loading"){
        setShouldPolling(true);
      } else {
        setShouldPolling(false);
      }
    }
  },[templateDetail])


  const {mutate: posthierarchy} = useMutation({mutationFn: async ({index}: {index: number}) => {
    return axios.post(`http://127.0.0.1:5000/e2e/templates/${id}/hierarchy`, {index: String(index)});
  }});
  const {mutate: postAction} = useMutation({mutationFn: async ({index,action}: {index: number, action:string}) => {
    return axios.post(`http://127.0.0.1:5000/e2e/templates/${id}/action`, {index: String(index), action});
  }});
  const {mutate:postRun, isPending:isRunPending} = useMutation({mutationFn: async () => {
    return axios.post(`http://127.0.0.1:5000/e2e/templates/${id}/run`);
  },
  onSuccess: () => {
    queryClient.invalidateQueries({queryKey: ['templates']});
  }
});

  const {mutate: postTask, isPending} = useMutation({ mutationFn: () => axios.post(`http://127.0.0.1:5000/e2e/templates/tasks`,{ object_id: id}), onSuccess:()=> {
    queryClient.invalidateQueries({queryKey: ['templates']});
  } })
  const theme = useTheme();
  const [open, setOpen] = useState(false);

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  const handlehierarchyButtonClick = (index: number) => () => {
    posthierarchy({index}, {onSuccess:()=> {
      queryClient.invalidateQueries({queryKey: ['templates', 'detail', id]})
    }});
  }

  const handleActionButtonClick = (index: number) => (action:string) => {
    postAction({index,action}, {onSuccess:()=> {
      queryClient.invalidateQueries({queryKey: ['templates', 'detail', id]})
    }});
  }

  return (
    <Box sx={{ display: 'flex', flexDirection:"column" }}>
      
      <Box flexGrow={1} padding={theme.spacing(3)} paddingTop={theme.spacing(10)} >

              <>
              <Box  display="flex" gap="20px" alignItems="center" marginBottom="15px">
                <Typography variant="h5" margin="0">
                  {templateDetail?.template_name}
                </Typography>
                <Button onClick={() =>{
                  postRun();
                  setShouldPolling(true);
                }}
                disabled={isRunPending || templateDetail?.run_status==="loading"}
                >
                  템플릿 실행
                </Button>
                <StatusIcon status={templateDetail?.run_status}/>
              </Box>
              <Box display="flex" gap="40px" alignItems="center" marginBottom="40px">
              {templateDetail?.template?.map((item,index) => item.ui_data !== undefined 
               ? (<Box key={item.ui_data|| index}  padding="5px"borderRadius="10px"bgcolor="#F8DEDE" width="200px" height="300px" display="flex" flexDirection="column" gap="10px"position="relative">
                <StatusIcon status={item.status}/>
                <Button variant="contained" onClick={handlehierarchyButtonClick(index)} sx={{position:"absolute", bottom: '-50px', left: "50%", transform: "translateX(-50%)", whiteSpace:"nowrap"}}>
                  화면정보등록
                  </Button>
                  {(item.screenshot_url) && <Image width={200} height={300} src={item.screenshot_url} alt="화면 이미지"/>}
                </Box>):
                <ActionBox key={index} action={item.action} status={item.status} onClick={handleActionButtonClick(index)}/>
              )}
              <Button variant="contained" disabled={isPending} onClick={() => {
                  postTask();
              }}>추가</Button>   
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
