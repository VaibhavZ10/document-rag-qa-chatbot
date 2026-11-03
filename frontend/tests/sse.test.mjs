import test from "node:test";
import assert from "node:assert/strict";
import { createSSEParser } from "../src/lib/sse.ts";

test("SSE events survive every possible packet split", () => {
  const input = ': heartbeat\r\n\r\nevent: token\r\ndata: {"content":"hello"}\r\n\r\nevent: done\ndata: {}\n\n';
  for (let i = 0; i <= input.length; i++) {
    const events = [];
    const parse = createSSEParser((e, d) => events.push([e, JSON.parse(d)]));
    parse(input.slice(0, i)); parse(input.slice(i));
    assert.deepEqual(events, [["token", { content: "hello" }], ["done", {}]]);
  }
});
test("one-character reads, multiline data and incomplete frames", () => {
  const events = [];
  const parse = createSSEParser((e,d) => events.push([e,d]));
  for (const c of 'data: first\ndata: second\n\nevent: token\ndata: incomplete') parse(c);
  assert.deepEqual(events, [["message", "first\nsecond"]]);
});
