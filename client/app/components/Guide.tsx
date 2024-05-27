import * as React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';

export default function Guide() {
  return (
    <div>
      <Typography>시나리오 생성 가이드</Typography>
      <Accordion>
        <AccordionSummary
          expandIcon={<ArrowDownwardIcon />}
          aria-controls="panel1-content"
          id="panel1-header"
        >
          <Typography>1. 디바이스 연결</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            컴퓨터와 안드로이드 디바이스를 유선 연결합니다. 상단의 디바이스 연결 확인 버튼을 이용해 연결 상태를 확인할 수 있습니다.
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary
          expandIcon={<ArrowDropDownIcon />}
          aria-controls="panel2-content"
          id="panel2-header"
        >
          <Typography>2. 화면 정보 등록</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            테스트하고자 하는 화면으로 디바이스를 조작한 뒤, 홤면 정보 등록 버튼을 눌러 화면 정보를 등록합니다.(몇 초 소요)
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary
          expandIcon={<ArrowDropDownIcon />}
          aria-controls="panel3-content"
          id="panel3-header"
        >
          <Typography>3. 액션 정보 등록</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography component="div">
            화면정보가 정상적으로 등록되면, 이후에 수행할 액션을 입력합니다. 입력가능한 명령어는 아래와 같습니다.
            <ul>
              <li>~~을 클릭해줘</li>
              <li>~~을 클릭해서 ~~을 입력해줘</li>
              <li>왼쪽으로 스와이프 해줘(위로, 애로, 오른쪽으로 가능</li>
              <li>홈으로 가줘</li>
              <li>뒤로 가줘</li>
            </ul>
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary
          expandIcon={<ArrowDropDownIcon />}
          aria-controls="panel4-content"
          id="panel4-header"
        >
          <Typography>4. 다음 화면 등록</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            액션 입력이 완료되면, 디바이스로 해당 액션을 수행한 뒤에 나타나는 화면을 다음 화면 등록창에 등록합니다.
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary
          expandIcon={<ArrowDropDownIcon />}
          aria-controls="panel5-content"
          id="panel5-header"
        >
          <Typography>5. 화면/액션 추가 </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            추가 버튼을 통해 화면과 액션을 추가할 수 있습니다.
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary
          expandIcon={<ArrowDropDownIcon />}
          aria-controls="panel6-content"
          id="panel6-header"
        >
          <Typography>6. 시나리오 실행</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            시나리오 구성이 완료되면 상단의 시나리오 실행 버튼을 클릭하고 성공여부를 확인합니다.
          </Typography>
        </AccordionDetails>
      </Accordion>
    </div>
  );
}