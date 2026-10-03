# GitChess

[English](README.md) | **한국어**

*Play chess together through GitHub Issues.*

GitHub 이슈와 Actions만으로 운영하는 커뮤니티 체스 프로젝트입니다. 자신의 저장소에 설치하면 참가자가 이동 링크로 이슈를 만들고, 봇이 수를 검증해 README의 체스판을 갱신합니다. 별도 서버나 API 키는 필요하지 않습니다.

**배포 기본값은 비활성화입니다.** 저장소 관리자가 `CHESS_ENABLED=true`를 설정해야 체스 워크플로가 실행됩니다.

## 빠른 시작

1. **Use this template → Create a new repository**로 자신의 저장소를 만듭니다. **Fork**하거나 코드를 복사해도 됩니다. 저장소 이름은 자유롭게 정할 수 있습니다.
2. **Settings → General → Features → Issues**를 활성화합니다.
3. **Settings → Actions → General**에서 GitHub Actions를 허용합니다. Fork한 경우 **Actions** 탭에서도 워크플로를 활성화하세요. 체스 워크플로는 `GITHUB_TOKEN`의 콘텐츠·이슈 쓰기 권한을 요청합니다.
4. **Settings → Secrets and variables → Actions → Variables**에 저장소 변수를 추가합니다.

   | 이름 | 값 |
   | :--- | :--- |
   | `CHESS_ENABLED` | `true` |

5. **Actions → GitChess → Run workflow**에서 기본 브랜치와 `new-game`을 선택해 실행합니다.
6. 실행이 끝나면 README를 새로고침합니다. 체스판과 이동 링크가 **자신의 저장소 주소**로 생성됩니다.

브랜치 보호 규칙을 사용하는 저장소에서는 봇이 대국 상태를 커밋·푸시할 수 있어야 합니다. 조직 정책으로 쓰기 권한이 제한된 경우 저장소 관리자가 해당 권한을 허용해야 합니다.

운영을 중지하려면 `CHESS_ENABLED` 변수를 삭제하거나 값을 `false`로 바꾸세요. 새 이슈와 수동 실행 모두 체스 작업을 건너뜁니다.

## 체스판

현재 상태: **<!-- BEGIN TURN -->설정 전<!-- END TURN -->**

`white`: 백 차례 · `black`: 흑 차례 · `game over`: 종료

<table>
<tr>
<td valign="top">

<!-- BEGIN CHESS BOARD -->
빠른 시작을 완료하면 체스판이 표시됩니다.
<!-- END CHESS BOARD -->

</td>
<td valign="top">

<!-- BEGIN MOVES LIST -->
새 게임을 시작하면 합법적인 이동 목록이 생성됩니다.
<!-- END MOVES LIST -->

</td>
</tr>
</table>

<!-- BEGIN GAME ACTIONS -->
초기 설정은 **Actions → GitChess → Run workflow → new-game**에서 진행하세요.
<!-- END GAME ACTIONS -->

## 플레이 방법

1. 체스판 옆 이동 목록에서 출발 칸(`FROM`)과 도착 칸(`TO`)을 고릅니다.
2. 도착 칸 링크를 클릭하고, 이슈 제목을 바꾸지 않은 채 제출합니다.
3. 봇이 이슈에 결과를 남기고 닫습니다. Actions 실행이 끝나면 README를 새로고침하세요.

- 참가자별 백·흑 배정은 없으며, 현재 차례의 기물을 누구나 움직일 수 있습니다.
- 같은 사용자가 두 번 연속으로 둘 수 없습니다.
- 합법적인 수만 허용됩니다. 캐슬링과 앙파상을 지원하며, 폰은 자동으로 퀸으로 승격합니다.
- 대국 종료 후에는 누구나 새 게임을 시작할 수 있습니다. 진행 중인 대국을 초기화할 수 있는 사람은 저장소 소유자입니다.
- 공개 저장소에서는 이슈를 만들 수 있는 사람이 참여할 수 있습니다. 비공개 저장소에서는 접근 권한이 있는 사용자끼리 플레이합니다.

직접 이슈를 만들 때 사용하는 제목:

```text
Chess: Move E2 to E4
Chess: Start new game
```

## 대국 관리

**Actions → GitChess → Run workflow**에서 다음 작업을 선택할 수 있습니다.

| 작업 | 동작 |
| :--- | :--- |
| `new-game` | 시작 배치로 초기화. 이동 기록은 초기화하고 참가자별 누적 이동 수는 유지 |
| `refresh` | 기존 대국을 유지하면서 체스판과 이슈 링크 갱신. 저장소 이름 변경 후 사용 |

배포 소스에는 개인 대국 데이터가 포함되어 있지 않습니다. 처음 설치할 때는 `new-game`으로 시작하세요.

## 로컬 실행 및 개발

Python 3.12 이상과 [uv](https://docs.astral.sh/uv/)가 필요합니다. `chess` 의존성은 스크립트 실행 시 자동으로 설치됩니다.

```sh
# 새 게임 시작: OWNER는 저장소 소유자의 GitHub 사용자명
uv run play.py seed OWNER OWNER/REPO

# 기존 대국을 유지하면서 README와 체스판 갱신
uv run play.py refresh OWNER/REPO

# 이슈 처리와 동일한 방식으로 한 수 두기
uv run play.py play "Chess: Move E2 to E4" PLAYER OWNER OWNER/REPO

# 테스트
uv run --with chess python -m unittest discover -s tests -v
```

로컬 명령은 `CHESS_ENABLED`와 관계없이 명시적으로 실행되며, 대국 상태·README·SVG를 갱신합니다. 실행 결과는 표준 출력과 `/tmp/chess-result.json`에 JSON으로 기록됩니다.

## 구성

| 경로 | 역할 |
| :--- | :--- |
| `play.py` | 이슈 명령 처리, 체스 규칙 검증, README·SVG 생성 |
| `README.md` / `README.ko.md` | 영어·한국어 안내와 함께 갱신되는 체스판 |
| `data/game.json` | 설치 후 생성되는 현재 배치(FEN), 이동 기록, 누적 이동 수 |
| `board-*.svg` | 설치 후 생성되는 체스판 이미지 |
| `.github/workflows/chess.yml` | 활성화된 저장소에서 이슈 및 수동 실행 처리 |
| `tests/` | 초기 설정·대국·렌더링 회귀 테스트 |

체스판·이동 목록·차례·새 게임 링크는 README의 `BEGIN` / `END` 주석 사이에서 자동 생성됩니다. 두 언어 문서는 함께 갱신되므로, README를 편집할 때 이 주석을 유지하세요.

버그 제보와 개선 제안은 이슈로, 코드 변경은 Pull Request로 보내주세요. 변경 후 위 테스트 명령으로 검증할 수 있습니다.

## 라이선스

[MIT License](LICENSE)
