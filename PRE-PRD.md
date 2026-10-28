사용 파일: boy.py, grass.py, main.py
사용할 이미지: animation_sheet.png, run_animation.png, grass.png
상태 다이어그램: state-machine.svg

구현해야 할 거
AutoRun 상태 추가
- a 키를 누르면 어떤 상태 든 바로 AutoRun 상태로 변경
- AutoRun 상태에서는 캐릭터의 크기가 커지고  속도가 run 상태보다 빨라짐
- AutoRun 상태에서 끝에 도달하면 방향이 전환된다.
- AutoRun 상태로 전환 시 5초 타이머가 작동하며 5초 타이머가 끝나면 IDLE 상태로 변경
- AutoRun 상태에서 방향키가 눌리면 일반 run 상태로 돌아감.
- 모든 구현이 완료된 후에는 state-macin.svg에 전체 상태 다이어그램을 나타내도록 한다.
- git 커밋은 최소 15번 이상 진행한다.