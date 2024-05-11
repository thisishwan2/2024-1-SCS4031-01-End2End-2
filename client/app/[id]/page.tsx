'use client'
import { Box, Button, CssBaseline, Divider, Drawer, IconButton, List, ListItem, ListItemButton, ListItemIcon, ListItemText, TextField, Toolbar, Typography, styled, useTheme } from "@mui/material";
import MenuIcon from '@mui/icons-material/Menu';
import MuiAppBar, { AppBarProps as MuiAppBarProps } from '@mui/material/AppBar';
import { useEffect, useState } from "react";
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import axios from "axios";
import Image from "next/image";

const drawerWidth = 240;

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })<{
  open?: boolean;
}>(({ theme, open }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  transition: theme.transitions.create('margin', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  marginLeft: `-${drawerWidth}px`,
  ...(open && {
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: 0,
  }),
}));

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

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

export default function Home() {
  const [actionText, setActionText] = useState('');
  const {id} = useParams();
  const queryClient= useQueryClient();
  const {data: scenarioDetail} = useQuery({queryKey: ['scenarios', 'detail', id], queryFn: async ()=> {
    const response =  await axios.get<{
      _id: string;
      run_status: string;
      scenario_name: string;
      scenario: {screenshot_url?:string; ui_data?: string; status?:string; action?:string}[]
    }>(`http://127.0.0.1:5000/e2e/scenarios/${id}`);
    return response.data;
  }})

  const {mutate: posthierarchy} = useMutation({mutationFn: async ({index}: {index: number}) => {
    return axios.post(`http://127.0.0.1:5000/e2e/scenarios/${id}/hierarchy`, {index: String(index)});
  }});
  const {mutate: postAction} = useMutation({mutationFn: async ({index,action}: {index: number, action:string}) => {
    return axios.post(`http://127.0.0.1:5000/e2e/scenarios/${id}/action`, {index: String(index), action});
  }});
  const {mutate:postRun} = useMutation({mutationFn: async () => {
    return axios.post(`http://127.0.0.1:5000/e2e/scenarios/${id}/run`);
  },});

  const {mutate: postTask, isPending} = useMutation({ mutationFn: () => axios.post(`http://127.0.0.1:5000/e2e/scenarios/tasks`,{ object_id: id}), onSuccess:()=> {
    queryClient.invalidateQueries({queryKey: ['scenarios']});
  } })
  const theme = useTheme();
  const [open, setOpen] = useState(false);
  const [scenario, setScenario] = useState([
    {
      id: 1,
      title: '시나리오 1',
      list: []
    }
  ]);

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  const handlehierarchyButtonClick = (index: number) => () => {
    posthierarchy({index}, {onSuccess:()=> {
      queryClient.invalidateQueries({queryKey: ['scenarios', 'detail', id]})
    }});
  }

  const handleActionButtonClick = (index: number) => () => {
    postAction({index,action:actionText}, {onSuccess:()=> {
      queryClient.invalidateQueries({queryKey: ['scenarios', 'detail', id]})
    }});
  }

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed" open={open}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
            sx={{ mr: 2, ...(open && { display: 'none' }) }}
          >
            <MenuIcon />
          </IconButton>
          

          <Typography variant="h6" noWrap component="div">
            QA 시나리오
          </Typography>

          
          
        </Toolbar>
      </AppBar>
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
        variant="persistent"
        anchor="left"
        open={open}
      >
        <DrawerHeader>
          <IconButton onClick={handleDrawerClose}>
            {theme.direction === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </DrawerHeader>
        <Divider />
        <List>
          {['시나리오 관리'].map((text, index) => (
            <ListItem key={text} disablePadding>
              <ListItemButton>
                <ListItemIcon>
                  {index % 2 === 0 ? <InboxIcon /> : <MailIcon />}
                </ListItemIcon>
                <ListItemText primary={text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        <Divider />
      </Drawer>
      <Main open={open}>
        <DrawerHeader />
         {
          scenario.map(item => {
            return (
              <>
              <Box key={item.id} display="flex" gap="20px" alignItems="center" marginBottom="15px">
                <Typography paragraph margin="0">
                  {item.title}
                </Typography>
                <Button onClick={() =>{
                  postRun();
                }}>
                  시나리오 실행
                </Button>
              </Box>
              <Box display="flex" gap="40px" alignItems="center" marginBottom="40px">
              {scenarioDetail?.scenario?.map((item,index) => item.ui_data !== undefined 
               ? (<Box key={item.ui_data|| index} bgcolor="lightgray" width="200px" height="300px" display="flex" flexDirection="column" gap="10px">
                <Button variant="contained" onClick={handlehierarchyButtonClick(index)}>
                  화면정보등록
                  </Button>
                  {(item.screenshot_url) && <Image width={200} height={300} src={item.screenshot_url} alt="화면 이미지"/>}
                </Box>):
                (<Box key={item.action||index} bgcolor="lightgray" width="200px" height="300px">
                  <TextField label="액션정보" value={actionText|| item.action} onChange={(e)=> {
                  setActionText(e.target.value);
                }} />
                <Button variant="contained" onClick={handleActionButtonClick(index)}>등록</Button>
              </Box>))}
              <Button variant="contained" disabled={isPending} onClick={() => {
                  postTask();
              }}>추가</Button>   
            </Box>
              </>
            )
          
          })
         }
      </Main>
    </Box>
  );
}