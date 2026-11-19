/* ---------- 比比（海牛）與 嚕嚕（海豹） ---------- */
const BIBI='#8E6A52', BIBI_DARK='#6E4F3C', LULU='#F4EEE2', NOSE_Y='#E2B23A', LULU_NOSE='#8A5A3C';

// 比比：趴著，頭朝左。opts: {sleep, flipper:'up'}
function bibiSVG(o={}){
  const body='M40 99 C19 99 9 86 12 73 C15 62 24 55 36 56 C40 40 56 27 82 27 C122 27 150 40 166 62 C172 70 179 73 189 70 C200 67 206 80 200 90 C194 98 181 97 172 92 C160 101 130 105 100 105 C72 105 52 101 40 99 Z';
  const s=[];
  s.push(`<ellipse cx="104" cy="107" rx="86" ry="5" fill="${SHADOW}" filter="url(#paint)"/>`);
  s.push(P(body,BIBI));
  s.push(L(body,1.15));
  s.push(L('M38 56 C46 66 48 84 44 99',.9,.75));             // 大鼻吻的分界
  s.push(L('M118 34 C126 46 128 66 124 86',.6,.3));           // 身體紋路
  if(o.flipper==='up') s.push(P('M84 92 C76 80 80 68 90 66 C96 74 96 86 92 96 Z',BIBI_DARK));
  else s.push(P('M80 102 C74 112 86 116 98 106 C94 103 88 102 80 102 Z',BIBI_DARK));
  s.push(`<circle cx="21" cy="69" r="2.8" fill="${NOSE_Y}"/>`);
  if(o.sleep) s.push(L('M55 50 q5 4 10 0',1.1));
  else s.push(`<circle cx="60" cy="50" r="2.8" fill="${INK}"/>`);
  return s.join('');
}

// 嚕嚕：坐著的圓胖身體。opts: {wink}
function luluSVG(o={}){
  const body='M60 12 C30 12 17 42 18 72 C19 106 27 127 41 130 C53 132 69 132 81 130 C95 127 102 106 102 72 C102 42 90 12 60 12 Z';
  const s=[];
  s.push(`<ellipse cx="60" cy="133" rx="44" ry="4" fill="${SHADOW}" filter="url(#paint)"/>`);
  s.push(P(body,LULU));
  s.push(L(body,1.15));
  s.push(L('M34 128 q6 7 13 1',1));                            // 小腳
  s.push(L('M73 129 q7 6 13 -1',1));
  s.push(L('M100 88 q9 6 6 16',1));                            // 側邊鰭
  // 臉
  if(o.wink) s.push(L('M42 48 q4 -4 8 0',1.2)); else s.push(`<circle cx="46" cy="49" r="3" fill="${INK}"/>`);
  s.push(`<circle cx="74" cy="49" r="3" fill="${INK}"/>`);
  s.push(`<path d="M57 53 L63 53 L60 57.5 Z" fill="${LULU_NOSE}"/>`);
  s.push(L('M54 60 q3 4 6 0 q3 4 6 0',1));
  s.push(L('M31 52 h6 M31 57 h6',.9,.8));                     // 鬍鬚
  s.push(L('M83 52 h6 M83 57 h6',.9,.8));
  return s.join('');
}

// 場景：組合角色，可加一杯飲料
function charScene(kind,drink){
  const w=(vb,inner,cls='')=>`<svg class="char ${cls}" viewBox="${vb}" xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden="true">${inner}</svg>`;
  const cup=(d,x,y,sc,ice)=>`<g transform="translate(${x} ${y}) scale(${sc})">${drawDrink(d,{ice:ice||'微冰'}).replace(/^<svg[^>]*>|<\/svg>$/g,'')}</g>`;
  switch(kind){
    case 'header':   // 比比趴在線上，嚕嚕靠在牠背後
      return w('0 0 330 120',`<g transform="translate(196 0) scale(.72)">${luluSVG({wink:true})}</g><g transform="translate(96 8)">${bibiSVG()}</g>`);
    case 'empty':    // 嚕嚕抱著空杯
      return w('0 0 160 150',`<g transform="translate(18 6)">${luluSVG()}</g>${cup({id:'empty',liquid:'#EDE6D8'},66,84,.3,'去冰')}`);
    case 'receipt':  // 兩個一起端飲料
      return w('0 0 330 150',`<g transform="translate(0 38)">${bibiSVG({flipper:'up'})}</g><g transform="translate(224 14) scale(.92)">${luluSVG()}</g>${cup(drink||byId.twglatte,168,64,.42,drink&&drink.__ice||'微冰')}`);
    case 'sleep':    // 比比睡覺
      return w('0 0 220 120',`${bibiSVG({sleep:true})}<text x="70" y="20" font-family="Lora,Georgia,serif" font-style="italic" font-size="15" fill="${INK}" opacity=".6">z z</text>`);
    case 'footer':   // 兩顆頭浮在水面
      return w('0 0 220 70',`<path d="M8 50 q20 -8 40 0 t40 0 t40 0 t40 0 t40 0" stroke="#7E95A0" stroke-width="1.3" fill="none" opacity=".7" filter="url(#line)"/>
        <clipPath id="sea"><rect x="0" y="0" width="220" height="49"/></clipPath>
        <g clip-path="url(#sea)"><g transform="translate(24 8) scale(.42)">${luluSVG()}</g><g transform="translate(96 16) scale(.5)">${bibiSVG()}</g></g>`);
  }
  return '';
}
