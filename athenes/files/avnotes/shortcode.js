// OSM Short links functions

// License: GNU General Public License 2.0, http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt

// makeShortCode taken from:
// https://github.com/openstreetmap/openstreetmap-website/blob/e84b2bd22f7c92fb7a128a91c999f86e350bf04d/app/assets/javascripts/application.js
// Important when using makeShortCode: provide args as numbers, not as strings!

function makeShortCode(lat, lon, zoom) {
  char_array = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_~";
  var x = Math.round((lon + 180.0) * ((1 << 30) / 90.0));
  var y = Math.round((lat + 90.0) * ((1 << 30) / 45.0));
  // JavaScript only has to keep 32 bits of bitwise operators, so this has to be
  // done in two parts. each of the parts c1/c2 has 30 bits of the total in it
  // and drops the last 4 bits of the full 64 bit Morton code.
  var str = "";
  var c1 = interleave(x >>> 17, y >>> 17), c2 = interleave((x >>> 2) & 0x7fff, (y >>> 2) & 0x7fff);
  for (var i = 0; i < Math.ceil((zoom + 8) / 3.0) && i < 5; ++i) {
    digit = (c1 >> (24 - 6 * i)) & 0x3f;
    str += char_array.charAt(digit);
  }
  for (var i = 5; i < Math.ceil((zoom + 8) / 3.0); ++i) {
    digit = (c2 >> (24 - 6 * (i - 5))) & 0x3f;
    str += char_array.charAt(digit);
  }
  for (var i = 0; i < ((zoom + 8) % 3); ++i) {
    str += "-";
  }
  return str;
}

function interleave(x, y) {
  x = (x | (x << 8)) & 0x00ff00ff;
  x = (x | (x << 4)) & 0x0f0f0f0f;
  x = (x | (x << 2)) & 0x33333333;
  x = (x | (x << 1)) & 0x55555555;
  y = (y | (y << 8)) & 0x00ff00ff;
  y = (y | (y << 4)) & 0x0f0f0f0f;
  y = (y | (y << 2)) & 0x33333333;
  y = (y | (y << 1)) & 0x55555555;
  return (x << 1) | y;
}

// decode function - not optimized for speed!

function decodeShortCode(sc) {
  char_array = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_~";
  var i=0;
  var x=0;
  var y=0;
  var z=-8;
  for(i=0;i<sc.length;i++) {
    ch=sc.charAt(i);
    digit=char_array.indexOf(ch);
    if(digit==-1) break;
    // distribute 6 bits into x and y
    x<<=3;
    y<<=3;
    for(j=2;j>=0;j--) {
      x |= ((digit & (1 << (j+j+1))) == 0 ? 0 : (1 << j));
      y |= ((digit & (1 << (j+j))) == 0 ? 0 : (1 << j));
    }
    z+=3;
  }
  x = x * Math.pow(2,2-3*i) * 90 - 180;
  y = y * Math.pow(2,2-3*i) * 45 -  90;
  // adjust z
  if(i<sc.length && sc.charAt(i)=="-") {
    z-=2;
    if(i+1<sc.length && sc.charAt(i+1)=="-") { z++; }
  }
  return new Array(y,x,z);
}
