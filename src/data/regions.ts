import regionsJson from "./regions.json";
import type { RegionScope } from "../types";

export interface Sigungu {
  code: string;
  name: string;
}

export interface Sido {
  code: string;
  name: string;
  sigungu: Sigungu[];
}

export const regionSource: string = regionsJson.source;
export const sidoList: Sido[] = regionsJson.sido;

export function findSido(code: string): Sido | undefined {
  return sidoList.find((s) => s.code === code);
}

export function regionLabel(region: RegionScope | null): string {
  if (!region) return "";
  if (region.level === "national") return "전국";
  const sido = findSido(region.sidoCode);
  if (!sido) return "";
  if (region.level === "sido") return sido.name;
  const sigungu = sido.sigungu.find((g) => g.code === region.sigunguCode);
  return sigungu ? `${sido.name} ${sigungu.name}` : sido.name;
}
