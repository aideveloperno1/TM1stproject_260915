// innerHTML 템플릿에 사용자 입력을 넣을 때 반드시 거친다.
export function esc(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function formatKrw(krw: number): string {
  return `${krw.toLocaleString("ko-KR")}원`;
}
