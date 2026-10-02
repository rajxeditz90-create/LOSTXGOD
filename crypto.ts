// Python 3 base64.b85decode exact implementation in TypeScript
// Alphabet: 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~

const B85_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~";
const B85_MAP: { [key: number]: number } = {};
for (let i = 0; i < B85_ALPHABET.length; i++) {
  B85_MAP[B85_ALPHABET.charCodeAt(i)] = i;
}

export function decodeB85(str: string): Uint8Array {
  // Clean whitespace/newlines
  const cleanStr = str.replace(/\s+/g, '');
  const padding = (-cleanStr.length % 5 + 5) % 5;
  const paddedStr = cleanStr + '~'.repeat(padding);

  const out: number[] = [];

  for (let i = 0; i < paddedStr.length; i += 5) {
    let acc = 0;
    for (let j = 0; j < 5; j++) {
      const code = paddedStr.charCodeAt(i + j);
      const digit = B85_MAP[code];
      if (digit === undefined) {
        throw new Error(`Bad base85 character '${paddedStr[i + j]}' at position ${i + j}`);
      }
      acc = acc * 85 + digit;
    }

    if (acc > 0xffffffff) {
      throw new Error(`Base85 overflow at chunk starting at position ${i}`);
    }

    // Pack big-endian 32-bit unsigned int into 4 bytes
    out.push((acc >>> 24) & 0xff);
    out.push((acc >>> 16) & 0xff);
    out.push((acc >>> 8) & 0xff);
    out.push(acc & 0xff);
  }

  const result = new Uint8Array(out);
  if (padding > 0) {
    return result.slice(0, result.length - padding);
  }
  return result;
}

export function hexToBytes(hex: string): Uint8Array {
  const cleanHex = hex.replace(/[^0-9a-fA-F]/g, '');
  const bytes = new Uint8Array(cleanHex.length / 2);
  for (let i = 0; i < bytes.length; i++) {
    bytes[i] = parseInt(cleanHex.substring(i * 2, i * 2 + 2), 16);
  }
  return bytes;
}

export function xorBytes(data: Uint8Array, key: Uint8Array): Uint8Array {
  if (key.length === 0) return data;
  const result = new Uint8Array(data.length);
  for (let i = 0; i < data.length; i++) {
    result[i] = data[i] ^ key[i % key.length];
  }
  return result;
}
