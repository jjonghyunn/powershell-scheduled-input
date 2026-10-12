# PowerShell 예약 자동 입력 도구

Windows 11 PowerShell에서 지정한 시간이 되면 대상 창을 활성화하고, 메시지 또는 TXT 파일 내용을 붙여 넣은 뒤 Enter 키를 자동으로 누르는 도구입니다.

현재 릴리스 버전: **v1.1.0**

PowerShell을 직접 사용하기 어렵거나 창 제목 뒤의 식별자가 계속 바뀌는 경우에는 `scheduled_input.py`를 사용하세요. `pipeline-26-2h-abc-defg`처럼 제목이 바뀌는 창도 상단 설정의 접두사만 지정하면 찾을 수 있습니다.

## 요구 사항

- Windows 11
- Windows PowerShell 5.1 또는 PowerShell 7
- 입력 대상 프로그램이 실행 중이고 화면에 보이는 창이어야 함

대상 프로그램이 관리자 권한으로 실행 중이면 이 스크립트도 관리자 권한으로 실행해야 할 수 있습니다. Windows의 권한 격리 기능 때문에 일반 권한 프로그램이 관리자 권한 창에 키 입력을 보내지 못할 수 있습니다.

## 사용 방법

PowerShell에서 현재 세션에만 스크립트 실행을 허용합니다.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

창 제목으로 대상 창을 찾아 메시지를 입력합니다.

```powershell
.\ScheduledInput.ps1 -At '2026-10-12 21:30' -WindowTitle '메모장' -Message '회의 자료를 확인해 주세요.'
```

프로세스 이름으로 대상을 지정하고 TXT 파일 내용을 입력합니다.

```powershell
.\ScheduledInput.ps1 -At '2026-10-12 21:30' -ProcessName 'notepad' -TextFile '.\message.txt'
```

텍스트만 붙여 넣고 Enter를 누르지 않으려면 `-NoEnter`를 추가합니다.

```powershell
.\ScheduledInput.ps1 -At '2026-10-12 21:30' -WindowTitle '메모장' -TextFile '.\message.txt' -NoEnter
```

## 주요 매개 변수

| 매개 변수 | 설명 |
| --- | --- |
| `-At` | 입력할 날짜와 시간입니다. 필수입니다. |
| `-Message` | 직접 입력할 메시지입니다. `-TextFile`과 함께 사용할 수 없습니다. |
| `-TextFile` | 읽어 올 TXT 파일 경로입니다. `-Message`와 함께 사용할 수 없습니다. |
| `-WindowTitle` | 활성화할 창 제목입니다. |
| `-ProcessName` | 활성화할 프로세스 이름입니다. 예: `notepad` |
| `-NoEnter` | 입력 후 Enter를 누르지 않습니다. |

`-WindowTitle`과 `-ProcessName` 중 하나는 반드시 지정해야 합니다. 대상 창이 예약 시각에 보이지 않으면 입력하지 않고 오류를 표시합니다.

## 동작 및 주의 사항

- 한글, 공백, 여러 줄 TXT 내용을 지원합니다.
- 입력에는 Windows 클립보드를 임시로 사용하고, 가능한 경우 기존 텍스트 내용을 복원합니다.
- 스크립트가 메시지를 PowerShell 명령으로 실행하지는 않습니다. 다만 대상 창을 PowerShell이나 터미널로 지정하면 해당 프로그램이 입력 내용을 명령으로 해석할 수 있습니다.
- 예약 시각에 다른 창이 앞에 나타나면 입력 대상이 달라질 수 있으므로 실행 중에는 대상 창의 상태를 확인하세요.

## 라이선스

MIT License

## Python 버전: 간단한 설정

### 설치

Windows 11에서 저장소 폴더를 연 뒤 다음 명령을 실행합니다.

```powershell
py -m pip install -r requirements.txt
```

### 설정 및 실행

`scheduled_input.py` 파일 상단의 `사용자 설정` 영역만 수정합니다.

```python
RUN_AT = "2026-10-12 19:05"  # 예약 시각: YYYY-MM-DD HH:MM 형식. 즉시 실행하려면 ""로 비워 두세요.
TEXT_FILE = r"C:\Users\CNXK\Downloads\리셋할일1.txt"
WINDOW_TITLE_PREFIX = "pipeline-26-2h-"
PRESS_ENTER = True
```

그 다음 아래 명령만 실행합니다.

```powershell
py scheduled_input.py
```

제목이 `pipeline-26-2h-abc-defg` 또는 `pipeline-26-2h-다른문자열`처럼 달라져도 `WINDOW_TITLE_PREFIX`에 지정한 부분으로 창을 찾습니다. 제목 앞에 `✳ ` 같은 표시가 붙어도 작동합니다. `PROCESS_NAMES`는 기본적으로 비어 있어 제목만으로 찾으며, 필요할 때만 프로세스 필터를 추가합니다.

직접 메시지를 사용하려면 `TEXT_FILE`을 빈 문자열로 바꾸고 `MESSAGE`에 내용을 입력합니다.

```python
TEXT_FILE = ""
MESSAGE = "입력할 메시지입니다."
```

Python 버전도 기본적으로 클립보드 붙여 넣기 후 Enter를 누르며, Enter를 생략하려면 `PRESS_ENTER = False`로 바꿉니다.
