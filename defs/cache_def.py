# %% [markdown]
# # 공용 캐시 함수
# ## file name
# - cache_def.py
#
# ## 기능
# - 모든 데이터 helper가 같이 쓰는 캐시 폴더 `codes/cache/<이름>`을 만들고, 날짜가 붙은 캐시 파일을 찾고 정리하는 함수 모음.
# - API 호출은 하지 않는다.
#
# ## 출처
# - 외부 자료 없음 (내부 유틸리티)
#
# ## 사용 예
# ```python
# # defs 경로 블록을 넣은 스크립트 또는 defs 안의 helper에서
# import os
# from datetime import date
# from cache_def import shared_cache_dir, prune_stale_cache, find_longer_cache, period_start
#
# cache_dir = shared_cache_dir("my_cache")            # codes/cache/my_cache (없으면 생성)
# cache_file = os.path.join(cache_dir, f"series_2020-01-01_{date.today()}.csv")
# # ... 받아서 cache_file에 저장한 직후
# prune_stale_cache(cache_file)                       # 어제 이전의 같은 이름 일별 캐시 삭제
#
# # 시작일만 더 이른 같은 시리즈 캐시 찾기 → start부터 잘라 쓰기
# longer = find_longer_cache(cache_dir, "2020-01-01", f"_{date.today()}.csv", prefix="series_")
# if longer:
#     df = pd.read_csv(longer, parse_dates=["Date"])
#     df = df[df["Date"] >= period_start("2020-01-01", "M")]
# ```
#
# ## 함수
# | Function | Returns | Description |
# |----------|---------|-------------|
# | `shared_cache_dir(name)` | `str` | `codes/cache/<name>` 폴더를 만들고 경로를 돌려준다. `'./x_cache'`, `'x_cache/'`처럼 써도 폴더 이름만 쓴다. 절대 경로는 그대로 |
# | `prune_stale_cache(cache_file)` | `int` | 이름의 마지막 날짜만 더 이르고 나머지가 같은 '그날 받은' 일별 캐시를 지우고 지운 개수를 돌려준다. 종료일을 고정한 캐시는 지우지 않는다 |
# | `find_longer_cache(folder, start, suffix, prefix=None)` | `str \| None` | 이름이 `prefix + 시작일 + suffix`이고 시작일만 더 이른 캐시 경로 (start에 가장 가까운 것) |
# | `period_start(start, cycle=None)` | `Timestamp` | 시작일을 M/Q/A 기간의 첫날로 바꾼다 (`'1999-Q1'` 표기도 받음). 긴 캐시를 자를 기준 |
# | `cache_fresh(path, end, final_days=365)` | `bool` | 종료일을 미래 고정일로 받는 캐시를 계속 써도 되는지: 오늘 저장했거나 저장일이 종료일보다 1년 넘게 뒤면 True |
#
# - `CACHE_ROOT`: 캐시 루트 경로 (`codes/cache`)
# - 날짜 토큰 형식: `2026-10-29`, `20261029`, `26_10_29`
#
# ## 사용하는 곳
# - defs의 데이터 helper 대부분 (fred, ecos, bis, imf, boj, mof, kosis 등)과 폴더 전용 helper (`wallstreet/nyfed_api_swap.py`, `gold/pykrx_api.py` 등)

# %%
# 캐시 정리 공통 함수
# 종료일을 오늘(date.today())로 받는 캐시는 날마다 새 파일이 생긴다.
# 새 캐시를 저장한 직후 prune_stale_cache(새 파일 경로)를 부르면,
# 이름은 같고 마지막 날짜만 더 이른 '그날그날 받은' 캐시 파일을 지운다.
# 종료일을 고정한 캐시(파일 날짜와 저장한 날이 다른 것)는 지우지 않는다.

import os
import re
from datetime import date, datetime
from pathlib import Path

# 모든 폴더가 같이 쓰는 캐시 루트: codes/cache/<캐시 이름>
CACHE_ROOT = Path(__file__).resolve().parent.parent / "cache"


def shared_cache_dir(name):
    """공용 캐시 폴더 codes/cache/<name>을 만들고 경로 문자열을 돌려준다.
    name은 'fred_cache', './nyfed_cache', 'imf_cache/'처럼 어떤 형식이든 폴더 이름만 쓴다.
    절대 경로를 주면 그 경로를 그대로 쓴다."""
    p = Path(name)
    if not p.is_absolute():
        p = CACHE_ROOT / p.name
    p.mkdir(parents=True, exist_ok=True)
    return str(p)

# 날짜 형식: 2026-10-29 / 20261029 / 26_10_29
_DATE_RE = re.compile(
    r"(?<!\d)(?:(19|20)(\d\d)-(\d\d)-(\d\d)|(19|20)(\d\d)(\d\d)(\d\d)|(\d\d)_(\d\d)_(\d\d))(?!\d)"
)


def _parse_date(m):
    g = m.groups()
    try:
        if g[0]:
            return date(int(g[0] + g[1]), int(g[2]), int(g[3]))
        if g[4]:
            return date(int(g[4] + g[5]), int(g[6]), int(g[7]))
        return date(2000 + int(g[8]), int(g[9]), int(g[10]))
    except ValueError:
        return None


def _last_date(name):
    """파일 이름의 마지막 날짜 토큰 (match, date). 없으면 (None, None)."""
    found = [(m, d) for m in _DATE_RE.finditer(name) if (d := _parse_date(m))]
    return found[-1] if found else (None, None)


def _written_on(path):
    return datetime.fromtimestamp(os.path.getmtime(path)).date()


def find_longer_cache(folder, start, suffix, prefix=None):
    """시작일만 더 이르고 나머지 이름이 같은 캐시 파일 경로 (없으면 None)

    파일 이름이 prefix + <시작일> + suffix 형태인 캐시에서,
    시작일 토큰이 start와 형식(숫자 자리)이 같고 start보다 이른 파일을 찾는다.
    여러 개면 start에 가장 가까운(가장 짧은) 파일을 고른다.
    prefix=None이면 앞부분은 비교하지 않는다 (ECOS처럼 이름표가 스크립트마다 다를 때).
    종료일 등 나머지 조건은 suffix에 넣어 정확히 일치시킨다.
    """
    start = str(start)
    shape = re.sub(r"\d", "0", start)
    if not re.search(r"\d", start):
        return None
    best = None
    try:
        names = os.listdir(folder)
    except OSError:
        return None
    for name in names:
        if not name.endswith(suffix) or len(name) <= len(suffix) + len(start):
            continue
        head = name[: len(name) - len(suffix)]
        token, rest = head[-len(start) :], head[: -len(start)]
        if prefix is not None and rest != prefix:
            continue
        if re.sub(r"\d", "0", token) == shape and token < start:
            if best is None or token > best[0]:
                best = (token, name)
    return os.path.join(folder, best[1]) if best else None


def cache_fresh(path, end, final_days=365):
    """종료일을 미래 고정일로 받는 캐시(이름만으로는 갱신 안 됨)를 계속 써도 되는지
    오늘 저장했거나, 저장일이 종료일보다 final_days일 넘게 뒤(확정된 과거 구간)면 True."""
    import pandas as pd

    written = _written_on(path)
    if written == date.today():
        return True
    try:
        return (written - pd.Timestamp(str(end)).date()).days > final_days
    except ValueError:
        return False


def period_start(start, cycle=None):
    """시작일 문자열을 cycle(M/Q/A) 기간의 첫날 Timestamp로 바꾼다.
    월·분기·연 자료는 날짜가 기간 첫날이라, 긴 캐시를 자를 때 이 값을 기준으로 쓴다.
    '1999-Q1' 같은 분기 표기도 받는다. cycle이 없거나 D면 그 날짜 그대로."""
    import pandas as pd

    start = str(start)
    ts = pd.Period(start).start_time if "Q" in start else pd.Timestamp(start)
    freq = {"M": "M", "Q": "Q", "A": "Y", "Y": "Y"}.get(cycle)
    return ts.to_period(freq).start_time if freq else ts


def prune_stale_cache(cache_file):
    """cache_file보다 날짜가 이른 같은 이름의 일별 캐시를 지우고, 지운 개수를 돌려준다.

    지우는 조건 (모두 만족):
    - 같은 폴더에 있고, 마지막 날짜 토큰만 다르고 나머지 이름이 같다.
    - 그 날짜가 cache_file의 날짜보다 이르다.
    - 그 날짜가 파일을 저장한 날과 하루 이내다 (= 종료일을 '오늘'로 받은 캐시).
    cache_file 자신도 오늘 받은 캐시일 때만 정리한다. 오류는 무시한다.
    """
    try:
        cache_file = str(cache_file)
        folder, name = os.path.split(cache_file)
        m, new_date = _last_date(name)
        if m is None or abs((_written_on(cache_file) - new_date).days) > 1:
            return 0
        prefix, suffix = name[: m.start()], name[m.end() :]
        removed = 0
        for other in os.listdir(folder or "."):
            if other == name or not (
                other.startswith(prefix) and other.endswith(suffix)
            ):
                continue
            om, old_date = _last_date(other)
            if om is None or other[: om.start()] != prefix or other[om.end() :] != suffix:
                continue
            path = os.path.join(folder, other)
            if old_date < new_date and abs((_written_on(path) - old_date).days) <= 1:
                os.remove(path)
                removed += 1
        return removed
    except OSError:
        return 0
