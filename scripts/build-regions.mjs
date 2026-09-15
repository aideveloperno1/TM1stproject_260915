// 주민등록인구 CSV(공개 자료)에서 시도·시군구 선택 목록을 만든다.
// 실행: npm run build:regions
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(here, "../../데이터/2/202601_202606_주민등록인구및세대현황_월간.csv");
const out = resolve(here, "../src/data/regions.json");

const text = new TextDecoder("euc-kr").decode(readFileSync(src));
const lines = text.split(/\r?\n/).slice(1).filter(Boolean);

const sidoList = [];
const bySido = new Map();

for (const line of lines) {
  const match = line.match(/^"([^"]+?)\s*\((\d{10})\)"/);
  if (!match) throw new Error(`행정구역 형식을 읽을 수 없음: ${line.slice(0, 60)}`);
  const [, rawName, code] = match;
  const name = rawName.trim().replace(/\s+/g, " ");
  // 6월 총인구수가 0인 코드(폐지 등)는 선택 목록에서 제외
  const juneTotal = line.split('","')[31]?.replace(/[",]/g, "").trim();
  if (juneTotal === "0") continue;

  const sidoCode = code.slice(0, 2);
  if (code.endsWith("00000000")) {
    const sido = { code, name, sigungu: [] };
    sidoList.push(sido);
    bySido.set(sidoCode, sido);
  } else {
    const sido = bySido.get(sidoCode);
    if (!sido) throw new Error(`상위 시도 없음: ${name}`);
    const sigunguName = name.slice(sido.name.length).trim();
    // 세종특별자치시처럼 시군구가 없는 단층 시도는 하위 목록을 비워 둔다
    if (sigunguName) sido.sigungu.push({ code, name: sigunguName });
  }
}

mkdirSync(dirname(out), { recursive: true });
writeFileSync(
  out,
  JSON.stringify({ source: "행정안전부 주민등록인구및세대현황 2026-06", sido: sidoList }, null, 2) + "\n",
);
console.log(`시도 ${sidoList.length}개, 시군구 ${sidoList.reduce((n, s) => n + s.sigungu.length, 0)}개 → ${out}`);
