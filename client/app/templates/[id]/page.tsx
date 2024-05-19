'use client'
import { Box, Button, CircularProgress, CssBaseline, Divider, Drawer, IconButton, List, ListItem, ListItemButton, ListItemIcon, ListItemText, TextField, Toolbar, Typography, styled, useTheme } from "@mui/material";

import MuiAppBar, { AppBarProps as MuiAppBarProps } from '@mui/material/AppBar';
import { useEffect, useState } from "react";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import axios from "axios";
import Image from "next/image";
import { BlockOutlined, CancelOutlined, CheckCircleOutline, CircleOutlined,  } from "@mui/icons-material";
import E2eSpaceIcon from '../../e2e-space.svg';

const drawerWidth = 240;

interface AppBarProps extends MuiAppBarProps {
  open?: boolean;
}

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})<AppBarProps>(({ theme, open }) => ({
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: `${drawerWidth}px`,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

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
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar color="transparent">
        <Toolbar>
          <E2eSpaceIcon />
          <List sx={{display:"flex",marginLeft:"30px" }}>
          {[{text: '시나리오 관리',href: "/"},{text: '템플릿 관리',href: "/templates"}].map(({text,href}, index) => (
            <ListItem key={text} disablePadding sx={{whiteSpace:"nowrap"}}>
              <ListItemButton href={href}>
                <ListItemText primary={text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

          
        </Toolbar>
      </AppBar>
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
               ? (<Box key={item.ui_data|| index} bgcolor="lightgray" width="200px" height="300px" display="flex" flexDirection="column" gap="10px">
                <StatusIcon status={item.status}/>
                <Button variant="contained" onClick={handlehierarchyButtonClick(index)}>
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
            
          

         <Button onClick={()=> {
          router.push("/templates")
         }} >목록으로</Button>
      </Box>
    </Box>
  );
}

const ActionBox = ({onClick, action, status}: {onClick:(action:string) => void; action?:string;status?:string}) => {

  const [actionText, setActionText] = useState('');
  const handleClick = () => {
    onClick(actionText);
  }
  return (<Box bgcolor="lightgray" width="200px" height="300px">
    <StatusIcon status={status}/>
    <TextField label="액션정보" value={actionText|| action} onChange={(e)=> {
     setActionText(e.target.value);
    }} />
    <Button variant="contained" onClick={handleClick}>등록</Button>
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
    status: <Icon />
  </Box>
}

const Loading = () => {
  return (
      <CircularProgress color="info" size={20} />
  );
};
