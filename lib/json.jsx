// ExtendScript 沒有原生 JSON：最小序列化器（物件、陣列、字串、數字、布林、null）
function J(v) {
  if (v === null || v === undefined) return 'null';
  var t = typeof v;
  if (t === 'number') return isFinite(v) ? String(v) : 'null';
  if (t === 'boolean') return v ? 'true' : 'false';
  if (t === 'string') {
    var s = '';
    for (var i = 0; i < v.length; i++) {
      var c = v.charAt(i), n = v.charCodeAt(i);
      if (c === '"') s += '\\"';
      else if (c === '\\') s += '\\\\';
      else if (n === 10) s += '\\n';
      else if (n === 13) s += '\\r';
      else if (n === 9) s += '\\t';
      else if (n < 32) s += ' ';
      else s += c;
    }
    return '"' + s + '"';
  }
  if (v instanceof Array) { var a = []; for (var i = 0; i < v.length; i++) a.push(J(v[i])); return '[' + a.join(',') + ']'; }
  var o = []; for (var k in v) o.push(J(String(k)) + ':' + J(v[k]));
  return '{' + o.join(',') + '}';
}
