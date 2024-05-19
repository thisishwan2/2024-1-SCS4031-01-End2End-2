import { AppBar, List, ListItem, ListItemButton, ListItemText, Toolbar } from "@mui/material"
import E2eSpaceIcon from '../e2e-space.svg';

const Header = () => {
  return (
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
  )
}

export default Header