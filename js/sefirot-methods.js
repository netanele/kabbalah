/* צבעי הספירות – מקום אחד לכל השיטות.
 * כל הצבעים של כל השיטות נמצאים כאן, והדפים קוראים מכאן. מעדכנים כאן בלבד.
 * המקור והלשון של כל שיטה: sefirot-colors.html (טבלת ההשוואה). "הצבעים שלנו": tzayach-shir-hasefirot.html.
 * colors[sefira]: c = צבעים (אחד או יותר), split = אחוז הצבע הראשון כשהוא "נוטה" לשני,
 *   kind: glow (אור לבן, כתר שלנו) | ring (תכלת עם טבעת קשת) | hidden (נעלם, בלי גוון) |
 *         all (כלול מכל גוון) | nocol (מתואר במילים, בלי צבע) | none (המקור אינו אומר דבר),
 *   t = לשון המקור בקצרה, alt = עוד גוונים שהמקור מזכיר.
 * השם הקדוש נשאר תמיד בספירה שלו (names); רק הגוון מתחלף לפי השיטה.
 */
(function(){
var DATA = {
 "sefirot": [
  {
   "id": "keter",
   "he": "כתר"
  },
  {
   "id": "chochma",
   "he": "חכמה"
  },
  {
   "id": "bina",
   "he": "בינה"
  },
  {
   "id": "chesed",
   "he": "חסד"
  },
  {
   "id": "gevura",
   "he": "גבורה"
  },
  {
   "id": "tiferet",
   "he": "תפארת"
  },
  {
   "id": "netzach",
   "he": "נצח"
  },
  {
   "id": "hod",
   "he": "הוד"
  },
  {
   "id": "yesod",
   "he": "יסוד"
  },
  {
   "id": "malchut",
   "he": "מלכות"
  }
 ],
 "names": {
  "אהי\"ה": "keter",
  "י\"ה": "chochma",
  "אלקים חיים": "bina",
  "אל": "chesed",
  "אלקים": "gevura",
  "הוי\"ה": "tiferet",
  "ה' צבאות": "netzach",
  "אלקים צבאות": "hod",
  "אל חי": "yesod",
  "אדנ\"י": "malchut"
 },
 "methods": [
  {
   "id": "shir",
   "name": "שיר הספירות",
   "ref": "ר' יוסף צייאח · הצבעים שלנו",
   "href": "tzayach-shir-hasefirot.html#song",
   "ours": true,
   "colors": {
    "keter": {
     "c": [
      "#ffffff",
      "#eee8da"
     ],
     "kind": "glow",
     "t": "לבן בוהק, בלתי נראה, כמו אוויר"
    },
    "chochma": {
     "c": [
      "#5b9bd5"
     ],
     "kind": "ring",
     "t": "תכלת, גוון הכולל כל הגוונים"
    },
    "bina": {
     "c": [
      "#f2c94c",
      "#3faa5a"
     ],
     "t": "צהוב וירוק"
    },
    "chesed": {
     "c": [
      "#ffffff",
      "#b9bec7"
     ],
     "t": "לבן וכסף"
    },
    "gevura": {
     "c": [
      "#c62828",
      "#d4a017"
     ],
     "t": "אדום וזהב"
    },
    "tiferet": {
     "c": [
      "#f2c94c",
      "#7e3fa6"
     ],
     "t": "צהוב וסגול"
    },
    "netzach": {
     "c": [
      "#f7b8cb"
     ],
     "t": "ורוד בהיר"
    },
    "hod": {
     "c": [
      "#b0305f"
     ],
     "t": "ורוד כהה"
    },
    "yesod": {
     "c": [
      "#f08a24"
     ],
     "t": "כתום"
    },
    "malchut": {
     "c": [
      "#1f4ea3"
     ],
     "t": "כחול"
    }
   }
  },
  {
   "id": "azriel",
   "name": "ר' עזריאל",
   "ref": "ביאור עשר ספירות, ט",
   "href": "sefirot-colors.html#azriel",
   "colors": {
    "keter": {
     "kind": "hidden",
     "t": "\"האור המתעלם\""
    },
    "chochma": {
     "c": [
      "#5b9bd5"
     ],
     "t": "\"הכולל כל גוון... כעין התכלת\""
    },
    "bina": {
     "c": [
      "#3faa5a"
     ],
     "t": "\"האור הירוק\""
    },
    "chesed": {
     "c": [
      "#ffffff"
     ],
     "t": "\"האור הלבן\""
    },
    "gevura": {
     "c": [
      "#c62828"
     ],
     "t": "\"האור האודם\""
    },
    "tiferet": {
     "c": [
      "#ffffff",
      "#c62828"
     ],
     "t": "\"כלול מלובן ואודם\""
    },
    "netzach": {
     "c": [
      "#c62828",
      "#ffffff"
     ],
     "split": 35,
     "t": "\"האודם הנוטה ללובן\""
    },
    "hod": {
     "c": [
      "#ffffff",
      "#c62828"
     ],
     "split": 35,
     "t": "\"הלובן הנוטה לאודם\""
    },
    "yesod": {
     "c": [
      "#ffffff",
      "#c62828"
     ],
     "t": "כלול מכולם"
    },
    "malchut": {
     "kind": "all",
     "t": "\"כלול מכל גוון\""
    }
   }
  },
  {
   "id": "tzintro",
   "name": "תיקוני זוהר, הקדמה",
   "ref": "א ע\"א",
   "href": "sefirot-colors.html#tzintro",
   "colors": {
    "keter": {
     "kind": "hidden",
     "t": "\"זהר טמיר וגניז\""
    },
    "chochma": {
     "kind": "nocol",
     "t": "\"זהר בהיר בשחקים\""
    },
    "bina": {
     "kind": "nocol",
     "t": "\"זריק נצוצין... כברק\""
    },
    "chesed": {
     "c": [
      "#ffffff"
     ],
     "t": "\"חוורו כסיהרא\""
    },
    "gevura": {
     "c": [
      "#c62828"
     ],
     "t": "\"סומקא כמאדים\""
    },
    "tiferet": {
     "c": [
      "#3faa5a"
     ],
     "t": "\"כליל ירוקא כחמה\""
    },
    "netzach": {
     "c": [
      "#3faa5a"
     ],
     "t": "\"ירוק כככב\""
    },
    "hod": {
     "c": [
      "#26221c",
      "#c62828"
     ],
     "t": "\"כליל אוכם וסומק\"",
     "alt": [
      "(בנוסח א: חוור וסומק)"
     ]
    },
    "yesod": {
     "kind": "nocol",
     "t": "\"זהיר לכל עיבר\""
    },
    "malchut": {
     "kind": "none"
    }
   }
  },
  {
   "id": "tz70",
   "name": "תיקון ע",
   "ref": "קכה ע\"א",
   "href": "sefirot-colors.html#tz70",
   "colors": {
    "keter": {
     "kind": "hidden",
     "t": "\"לא אשתמודע ביה גוון כלל\""
    },
    "chochma": {
     "kind": "none"
    },
    "bina": {
     "c": [
      "#26221c"
     ],
     "t": "אוכם, \"מסטרא דאימא עלאה\""
    },
    "chesed": {
     "c": [
      "#ffffff"
     ],
     "t": "חוור"
    },
    "gevura": {
     "c": [
      "#c62828"
     ],
     "t": "סומק"
    },
    "tiferet": {
     "c": [
      "#3faa5a"
     ],
     "t": "ירוק, \"עמודא דאמצעיתא\""
    },
    "netzach": {
     "c": [
      "#ffffff"
     ],
     "t": "נוטל מן הימין"
    },
    "hod": {
     "c": [
      "#c62828"
     ],
     "t": "נוטל מן השמאל"
    },
    "yesod": {
     "c": [
      "#3faa5a"
     ],
     "t": "\"נטיל גוון מגופא\""
    },
    "malchut": {
     "c": [
      "#26221c"
     ],
     "t": "\"אימא תתאה נטילת גוון מאימא עלאה\""
    }
   }
  },
  {
   "id": "tzeye",
   "name": "תיקון ע, גווני העין",
   "ref": "קכח ע\"ב",
   "href": "sefirot-colors.html#tzeye",
   "colors": {
    "keter": {
     "kind": "none"
    },
    "chochma": {
     "kind": "none"
    },
    "bina": {
     "kind": "none"
    },
    "chesed": {
     "c": [
      "#ffffff"
     ],
     "t": "לבנה"
    },
    "gevura": {
     "c": [
      "#c62828"
     ],
     "t": "מאדים"
    },
    "tiferet": {
     "c": [
      "#3faa5a"
     ],
     "t": "חמה"
    },
    "netzach": {
     "kind": "nocol",
     "t": "\"כרובי עינא\" – נוגה"
    },
    "hod": {
     "kind": "nocol",
     "t": "\"כרובי עינא\" – כוכב"
    },
    "yesod": {
     "c": [
      "#26221c"
     ],
     "t": "שבתאי"
    },
    "malchut": {
     "c": [
      "#5b9bd5"
     ],
     "t": "צדק"
    }
   }
  },
  {
   "id": "zohar",
   "name": "הזוהר",
   "ref": "קשת, נר, ציצית",
   "href": "sefirot-colors.html#zohar",
   "colors": {
    "keter": {
     "kind": "none"
    },
    "chochma": {
     "kind": "none"
    },
    "bina": {
     "kind": "none"
    },
    "chesed": {
     "c": [
      "#ffffff"
     ],
     "t": "\"חוור מימינא\""
    },
    "gevura": {
     "c": [
      "#5b9bd5"
     ],
     "t": "\"תכלת משמאלא\" (ציצית)"
    },
    "tiferet": {
     "c": [
      "#3faa5a"
     ],
     "t": "\"עמודא דאמצעיתא... ירוק\"",
     "alt": [
      "יה\"ו – \"נהורא חוורא\""
     ]
    },
    "netzach": {
     "kind": "none"
    },
    "hod": {
     "kind": "none"
    },
    "yesod": {
     "c": [
      "#ffffff",
      "#c62828",
      "#3faa5a"
     ],
     "t": "הקשת – \"חיור וסומק וירוק\""
    },
    "malchut": {
     "c": [
      "#5b9bd5",
      "#26221c"
     ],
     "t": "\"נהורא תכלא אוכמא\", לזמנין סומקא",
     "alt": [
      "תכלת – כרסייא"
     ]
    }
   }
  },
  {
   "id": "maarechet",
   "name": "מערכת האלהות",
   "ref": "פרקים ד, י\"ב",
   "href": "sefirot-colors.html#maarechet",
   "colors": {
    "keter": {
     "kind": "none"
    },
    "chochma": {
     "kind": "none"
    },
    "bina": {
     "c": [
      "#3faa5a"
     ],
     "t": "\"קו ירוק\""
    },
    "chesed": {
     "c": [
      "#ffffff"
     ],
     "t": "\"כל דבר לבן\"",
     "alt": [
      "כסף"
     ]
    },
    "gevura": {
     "c": [
      "#d4a017"
     ],
     "t": "\"דין זהב\""
    },
    "tiferet": {
     "c": [
      "#ffffff"
     ],
     "t": "\"אש לבנה\"",
     "alt": [
      "ברזל"
     ]
    },
    "netzach": {
     "kind": "none"
    },
    "hod": {
     "kind": "none"
    },
    "yesod": {
     "kind": "none"
    },
    "malchut": {
     "c": [
      "#5b9bd5"
     ],
     "t": "\"תכלת... כלולה בכל\"",
     "alt": [
      "\"דין רפה\"",
      "ארגמן",
      "\"אש שחורה\""
     ]
    }
   }
  },
  {
   "id": "gikatilla",
   "name": "ר' יוסף ג'יקטילה",
   "ref": "שערי אורה",
   "href": "sefirot-colors.html#gikatilla",
   "colors": {
    "keter": {
     "c": [
      "#ffffff"
     ],
     "t": "\"בתכליתה לובן\""
    },
    "chochma": {
     "kind": "none"
    },
    "bina": {
     "kind": "none"
    },
    "chesed": {
     "kind": "none"
    },
    "gevura": {
     "kind": "none"
    },
    "tiferet": {
     "kind": "none"
    },
    "netzach": {
     "kind": "none"
    },
    "hod": {
     "kind": "none"
    },
    "yesod": {
     "kind": "none"
    },
    "malchut": {
     "c": [
      "#3faa5a"
     ],
     "t": "אדנ\"י – \"אש ירוקה\"",
     "alt": [
      "שד\"י – \"אש שחורה\"",
      "אלהי\"ם – \"אש אדומה\""
     ]
    }
   }
  },
  {
   "id": "ramak",
   "name": "הרמ\"ק",
   "ref": "פרדס רמונים י; אור נערב ו",
   "href": "sefirot-colors.html#ramak",
   "colors": {
    "keter": {
     "c": [
      "#ffffff"
     ],
     "t": "\"לובן בתכלית\"",
     "alt": [
      "שחור, כלפי המאציל",
      "בלי גוון, בעצמו"
     ]
    },
    "chochma": {
     "c": [
      "#5b9bd5"
     ],
     "t": "תכלת או ספיר, \"ראש לכל הגוונים\""
    },
    "bina": {
     "c": [
      "#3faa5a"
     ],
     "t": "\"הירוק כעשבים\""
    },
    "chesed": {
     "c": [
      "#b9bec7"
     ],
     "t": "\"לבן קרוב אל התכלת... הכסף\""
    },
    "gevura": {
     "c": [
      "#c62828"
     ],
     "t": "אודם",
     "alt": [
      "שחור",
      "תכלת",
      "זהב"
     ]
    },
    "tiferet": {
     "c": [
      "#ffffff",
      "#c62828"
     ],
     "t": "לבן ואדום",
     "alt": [
      "\"ירוק כחלמון ביצה\"",
      "ארגמן"
     ]
    },
    "netzach": {
     "c": [
      "#c62828",
      "#ffffff"
     ],
     "split": 35,
     "t": "\"אודם נוטה אל הלובן\""
    },
    "hod": {
     "c": [
      "#ffffff",
      "#c62828"
     ],
     "split": 35,
     "t": "\"לובן נוטה אל האודם\""
    },
    "yesod": {
     "c": [
      "#ffffff",
      "#c62828"
     ],
     "t": "\"גוון תערובת\"",
     "alt": [
      "כלול מכל"
     ]
    },
    "malchut": {
     "kind": "all",
     "t": "כלולה מכל גוון",
     "alt": [
      "תכלת"
     ]
    }
   }
  }
 ]
};

var RAINBOW = ['#ffffff','#5b9bd5','#3faa5a','#f2c94c','#c62828','#7e3fa6'];
function lum(h){h=h.replace('#','');if(h.length===3)h=h.split('').map(function(x){return x+x}).join('');
  var r=parseInt(h.substr(0,2),16)/255,g=parseInt(h.substr(2,2),16)/255,b=parseInt(h.substr(4,2),16)/255;
  return .2126*r+.7152*g+.0722*b;}
function stops(cs,split,dir){
  if(cs.length===2&&split) return 'linear-gradient('+dir+','+cs[0]+' '+split+'%,'+cs[1]+' '+split+'%)';
  var n=cs.length,p=[];cs.forEach(function(c,i){p.push(c+' '+Math.round(i*100/n)+'%',c+' '+Math.round((i+1)*100/n)+'%');});
  return 'linear-gradient('+dir+','+p.join(',')+')';}
/* CSS לאותיות שם בגוון הספירה */
function letterCss(e){
  var k=e.kind||'';
  if(k==='none'||k==='nocol') return 'color:#b3a994;background:none;-webkit-text-stroke:0;text-shadow:none;filter:none';
  if(k==='hidden') return 'color:transparent;background:none;-webkit-text-stroke:1px #9c7a33;text-shadow:none;filter:none;opacity:.85';
  var cs=k==='all'?RAINBOW:e.c, light=cs.every(function(c){return lum(c)>.8});
  var stroke=light?'-webkit-text-stroke:1px #b39a5e;':'-webkit-text-stroke:.6px #4a2d0f55;';
  if(k==='glow') return 'color:#fffdf5;background:none;-webkit-text-stroke:1.1px #b39a5e;text-shadow:0 0 14px #fff3cc,0 0 3px #efe3c2;filter:none';
  if(cs.length===1) return 'color:'+cs[0]+';background:none;'+stroke+'text-shadow:none;filter:none';
  return 'background:'+stops(cs,e.split,'180deg')+';-webkit-background-clip:text;background-clip:text;color:transparent;'+stroke+'text-shadow:none;filter:none';}
/* CSS לשם בתוך הטקסט (גלולה בגוון הספירה) */
function pillCss(e){
  var k=e.kind||'';
  if(k==='none'||k==='nocol') return 'background:#ece5d6;color:#8a7f6d;border:1px dashed #c9bda5;text-shadow:none';
  if(k==='hidden') return 'background:transparent;color:#6f665a;border:1px dashed #9c7a33;text-shadow:none';
  var cs=k==='all'?RAINBOW:e.c;
  var bg=k==='glow'?'radial-gradient(#fff,#f1ebdc)':k==='all'?'conic-gradient('+RAINBOW.concat(['#ffffff']).join(',')+')':cs.length===1?cs[0]:stops(cs,e.split,'135deg');
  var avg=cs.reduce(function(a,c){return a+lum(c)},0)/cs.length;
  var fg=avg>.62?'color:#3a2e1d;text-shadow:0 0 2px #fff,0 0 2px #fff':'color:#fff;text-shadow:0 0 2px #1d1408,0 0 2px #1d1408,0 0 4px #1d1408';
  var border=k==='glow'?'border:1px dashed #cbbd9c':(avg>.8?'border:1px solid #c9bda5':'border:1px solid transparent');
  return 'background:'+bg+';'+fg+';'+border;}
/* דוגמית עגולה */
function swatch(e){
  var k=e.kind||'';
  if(k==='none') return 'background:#f4f0e6;border:1px dashed #c9bda5';
  if(k==='nocol'||k==='hidden') return 'background:transparent;border:1px dashed #9c7a33';
  if(k==='glow') return 'background:radial-gradient(#fff,#eee8da);border:1px dashed #cbbd9c';
  if(k==='ring') return 'background:'+e.c[0]+';box-shadow:0 0 0 2px #fdd835,0 0 0 4px #e53935';
  if(k==='all') return 'background:conic-gradient('+RAINBOW.concat(['#ffffff']).join(',')+')';
  var cs=e.c; return 'background:'+(cs.length===1?cs[0]:stops(cs,e.split,'135deg'))+';border:1px solid '+(cs.every(function(c){return lum(c)>.8})?'#cbbd9c':'#0003');}
function method(id){for(var i=0;i<DATA.methods.length;i++) if(DATA.methods[i].id===id) return DATA.methods[i]; return DATA.methods[0];}
window.SEFIROT = {data:DATA, method:method, letterCss:letterCss, pillCss:pillCss, swatch:swatch,
  label:function(e){return e.kind==='none'?'המקור אינו אומר דבר על ספירה זו':e.t+(e.alt?' · '+e.alt.join(' · '):'');}};
})();
