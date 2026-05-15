/**
 * 올림픽기념국민생활관 2026년 5월 운영·접수 일정 (공지 캘린더 기준).
 * 텔레그램 브릿지/봇에서 웹의「준비중」만 보고「등록 가능 수업 없음」으로 오인하지 않도록 안내 문구를 만듭니다.
 */
(function (root) {
  const VENUE = '올림픽기념국민생활관';
  const MONTH_TITLE = '2026년 5월';

  /** @type {{ day: number; label: string }[]} */
  const CLOSURE_DAYS = [
    { day: 1, label: '근로자의 날' },
    { day: 5, label: '어린이날' },
    { day: 25, label: '대체공휴일(부처님 오신 날 대체)' },
    { day: 28, label: '정기휴관일' },
  ];

  const EXISTING_MEMBER_DAYS = new Set([16, 18, 19, 20]);
  const NEW_MEMBER_FIRST_DAY = 22;

  function seoulCalendarParts(date) {
    const d = date instanceof Date ? date : new Date(date);
    const ymd = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Seoul',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).format(d);
    const [y, m, day] = ymd.split('-').map((x) => parseInt(x, 10));
    const weekday = new Intl.DateTimeFormat('ko-KR', { timeZone: 'Asia/Seoul', weekday: 'short' }).format(d);
    return { y, m, day, weekday };
  }

  function findClosure(day) {
    return CLOSURE_DAYS.find((c) => c.day === day) || null;
  }

  /**
   * @param {Date} [now]
   * @returns {string}
   */
  function getOlympicLifeCenterMay2026TelegramMessage(now = new Date()) {
    const { y, m, day, weekday } = seoulCalendarParts(now);

    const header = `🏊 ${VENUE} · ${MONTH_TITLE} 수강·접수 안내`;
    const common =
      `웹에서 프로그램이 모두「준비중」으로 보여도, 접수 오픈 전이거나 휴관일이면 정상일 수 있습니다. 아래는 당월 공지 캘린더 기준입니다.\n\n` +
      `📌 접수(5월)\n` +
      `· 기존 회원: 5/16(토), 5/18(월)~5/20(수)\n` +
      `· 신규 회원: 5/22(금)부터 (정원 마감 시까지)\n\n` +
      `🏝 5월 휴관\n` +
      CLOSURE_DAYS.map((c) => `· 5/${String(c.day).padStart(2, '0')} ${c.label}`).join('\n') +
      `\n\n` +
      `📎 접수 시각·방법은 홈페이지「접수안내」를 확인하세요.\n` +
      `※ 일요일 일일입장은 잠정 중단(공지 기준)입니다.`;

    if (y !== 2026 || m !== 5) {
      return (
        `${header}\n\n` +
        `이 일정표는 ${MONTH_TITLE} 기준입니다. 다른 달은 시설 홈페이지 운영일정을 확인해 주세요.\n\n` +
        common
      );
    }

    const closure = findClosure(day);
    if (closure) {
      return (
        `${header}\n\n` +
        `오늘(5/${day} ${weekday})은 휴관일입니다 (${closure.label}).\n\n` +
        common
      );
    }

    let phase = '';
    if (day < 16) {
      phase = `오늘은 아직 기존 회원 접수 첫날(5/16) 전입니다. 곧 공지된 일정에 맞춰 접수가 열립니다.`;
    } else if (day >= 16 && day <= 20) {
      if (EXISTING_MEMBER_DAYS.has(day)) {
        phase = `오늘(5/${day} ${weekday})은 기존 회원 접수일입니다. 웹 반영이 늦으면 잠시「준비중」으로 보일 수 있습니다.`;
      } else {
        phase = `오늘(5/${day} ${weekday})은 달력상 기존 회원 접수일이 아닙니다. (기존: 5/16, 5/18~20) 신규 접수는 5/22(금)부터입니다.`;
      }
    } else if (day >= NEW_MEMBER_FIRST_DAY) {
      phase = `5/22(금)부터는 신규 회원 접수 기간입니다(정원 마감 시까지). 웹이「준비중」이면 오픈 직전이거나 접속 지연일 수 있으니 접수안내 시간을 확인하세요.`;
    } else {
      phase = `기존 회원 접수(5/20까지)와 신규 접수 시작(5/22) 사이 구간입니다. 신규는 5/22(금)부터입니다.`;
    }

    return `${header}\n\n${phase}\n\n${common}`;
  }

  root.getOlympicLifeCenterMay2026TelegramMessage = getOlympicLifeCenterMay2026TelegramMessage;
})(typeof globalThis !== 'undefined' ? globalThis : typeof window !== 'undefined' ? window : this);
