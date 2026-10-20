/* צבעי הספירות – המקום האחד של כל השיטות.
 *
 * כל הצבעים של כל השיטות כתובים כאן בלבד, וכל הדפים צובעים מכאן:
 *   - טבלת ההשוואה בדף sefirot-colors.html נבנית מהנתונים האלה,
 *   - העץ, הטבלה והרשימה בדף שיר הספירות, הייחודים באוצר הייחודים והעצים בדף הבית נצבעים מהם,
 *   - ודוגמיות הצבע של שיטת הרמ"ק בדף המדיטציה (data-sef-list="ramak") נבנות מהם.
 * כדי לשנות צבע: משנים כאן, וכל הדפים מתעדכנים. כדי להוסיף שיטה: מוסיפים בלוק למטה (וקטע עם לשון המקור בדף sefirot-colors.html).
 *
 * לכל שיטה: id, name ו־ref (לרשימת הבחירה), href (לשון המקור), col ו־colRef (כותרת העמודה בטבלת ההשוואה).
 * לכל ספירה: chips = מה שהמקור אומר, בסדר שבטבלה. כל chip:
 *   c = צבעים (אחד, שניים או שלושה), split = אחוז הצבע הראשון כשהוא "נוטה" לשני,
 *   kind: glow (אור לבן, הכתר שלנו) | ring (תכלת עם טבעת קשת, החכמה שלנו) | hidden (נעלם, בלי גוון) |
 *         all (כלול מכל גוון) | nocol (מתואר במילים, בלי צבע),
 *   t = לשון המקור בקצרה, title = שם הגוון.
 *   use = איזה chip צובע את השמות (ברירת מחדל: הראשון שיש לו צבע); t ברמת הספירה = תיאור ארוך יותר.
 *   ספירה בלי chips = המקור אינו אומר עליה דבר.
 * השם הקדוש נשאר תמיד בספירה שלו (names); רק הגוון מתחלף לפי השיטה.
 */
(function(){
var METHODS = [
  {id:"shir", name:"שיר הספירות", ref:"ר' יוסף צייאח · הצבעים שלנו", href:"tzayach-shir-hasefirot.html#song", col:"שיר הספירות", colRef:"הצבעים שלנו", ours:true, colors:{
    keter: {"chips": [{"kind": "glow", "c": ["#fff", "#eee8da"], "t": "לבן בוהק, כמו אוויר"}], "t": "לבן בוהק, בלתי נראה, כמו אוויר"},
    chochma: {"chips": [{"kind": "ring", "c": ["#5b9bd5"], "t": "תכלת, כולל כל הגוונים"}], "t": "תכלת, גוון הכולל כל הגוונים"},
    bina: {"chips": [{"c": ["#f2c94c", "#3faa5a"], "t": "צהוב וירוק"}], "t": "צהוב וירוק"},
    chesed: {"chips": [{"c": ["#fff", "#b9bec7"], "t": "לבן וכסף"}], "t": "לבן וכסף"},
    gevura: {"chips": [{"c": ["#c62828", "#d4a017"], "t": "אדום וזהב"}], "t": "אדום וזהב"},
    tiferet: {"chips": [{"c": ["#f2c94c", "#7e3fa6"], "t": "צהוב וסגול"}], "t": "צהוב וסגול"},
    netzach: {"chips": [{"c": ["#f7b8cb"], "t": "ורוד בהיר"}], "t": "ורוד בהיר"},
    hod: {"chips": [{"c": ["#b0305f"], "t": "ורוד כהה"}], "t": "ורוד כהה"},
    yesod: {"chips": [{"c": ["#f08a24"], "t": "כתום"}], "t": "כתום"},
    malchut: {"chips": [{"c": ["#1f4ea3"], "t": "כחול"}], "t": "כחול"}
  }},
  {id:"azriel", name:"ר' עזריאל", ref:"ביאור עשר ספירות, ט", href:"sefirot-colors.html#azriel", col:"ר' עזריאל", colRef:"ביאור עשר ספירות ט", colors:{
    keter: {"chips": [{"kind": "hidden", "title": "נעלם, בלי גוון", "t": "\"האור המתעלם\""}]},
    chochma: {"chips": [{"c": ["#5b9bd5"], "title": "תכלת", "t": "\"הכולל כל גוון... כעין התכלת\""}]},
    bina: {"chips": [{"c": ["#3faa5a"], "title": "ירוק", "t": "\"האור הירוק\""}]},
    chesed: {"chips": [{"c": ["#fff"], "title": "לבן", "t": "\"האור הלבן\""}]},
    gevura: {"chips": [{"c": ["#c62828"], "title": "אדום", "t": "\"האור האודם\""}]},
    tiferet: {"chips": [{"c": ["#fff", "#c62828"], "title": "לבן ואדום", "t": "\"כלול מלובן ואודם\""}]},
    netzach: {"chips": [{"c": ["#c62828", "#fff"], "split": 35, "title": "אדום נוטה ללבן", "t": "\"האודם הנוטה ללובן\""}]},
    hod: {"chips": [{"c": ["#fff", "#c62828"], "split": 35, "title": "לבן נוטה לאדום", "t": "\"הלובן הנוטה לאודם\""}]},
    yesod: {"chips": [{"c": ["#fff", "#c62828"], "title": "לבן ואדום", "t": "\"כלול מלובן ואודם\" ומנטיותיהם"}]},
    malchut: {"chips": [{"kind": "all", "title": "כלול מכל גוון", "t": "\"כלול מכל גוון\""}]}
  }},
  {id:"tzintro", name:"תיקוני זוהר, הקדמה", ref:"א ע\"א", href:"sefirot-colors.html#tzintro", col:"תיקוני זוהר", colRef:"הקדמה, א ע\"א", colors:{
    keter: {"chips": [{"kind": "hidden", "title": "נעלם, בלי גוון", "t": "\"זהר טמיר וגניז\""}]},
    chochma: {"chips": [{"kind": "nocol", "t": "\"זהר בהיר בשחקים\""}]},
    bina: {"chips": [{"kind": "nocol", "t": "\"זריק נצוצין... כברק\""}]},
    chesed: {"chips": [{"c": ["#fff"], "title": "לבן", "t": "\"חוורו כסיהרא\""}]},
    gevura: {"chips": [{"c": ["#c62828"], "title": "אדום", "t": "\"סומקא כמאדים\""}]},
    tiferet: {"chips": [{"c": ["#3faa5a"], "title": "ירוק", "t": "\"כליל ירוקא כחמה\""}]},
    netzach: {"chips": [{"c": ["#3faa5a"], "title": "ירוק", "t": "\"ירוק כככב\""}]},
    hod: {"chips": [{"c": ["#26221c", "#c62828"], "title": "שחור ואדום", "t": "\"כליל אוכם וסומק\""}, {"kind": "nocol", "t": "(בנוסח א: חוור וסומק)"}]},
    yesod: {"chips": [{"kind": "nocol", "t": "\"זהיר לכל עיבר\""}]},
    malchut: {"chips": []}
  }},
  {id:"tz70", name:"תיקון ע", ref:"קכה ע\"א", href:"sefirot-colors.html#tz70", col:"תיקון ע", colRef:"קכה ע\"א", colors:{
    keter: {"chips": [{"kind": "hidden", "title": "נעלם, בלי גוון", "t": "\"לא אשתמודע ביה גוון כלל\""}]},
    chochma: {"chips": []},
    bina: {"chips": [{"c": ["#26221c"], "title": "שחור", "t": "אוכם, \"מסטרא דאימא עלאה\""}]},
    chesed: {"chips": [{"c": ["#fff"], "title": "לבן", "t": "חוור"}]},
    gevura: {"chips": [{"c": ["#c62828"], "title": "אדום", "t": "סומק"}]},
    tiferet: {"chips": [{"c": ["#3faa5a"], "title": "ירוק", "t": "ירוק, \"עמודא דאמצעיתא\""}]},
    netzach: {"chips": [{"c": ["#fff"], "title": "לבן", "t": "נוטל מן הימין"}]},
    hod: {"chips": [{"c": ["#c62828"], "title": "אדום", "t": "נוטל מן השמאל"}]},
    yesod: {"chips": [{"c": ["#3faa5a"], "title": "ירוק", "t": "\"נטיל גוון מגופא\""}]},
    malchut: {"chips": [{"c": ["#26221c"], "title": "שחור", "t": "\"אימא תתאה נטילת גוון מאימא עלאה\""}]}
  }},
  {id:"tzeye", name:"תיקון ע, גווני העין", ref:"קכח ע\"ב", href:"sefirot-colors.html#tzeye", col:"תיקון ע", colRef:"גווני העין, קכח ע\"ב", colors:{
    keter: {"chips": []},
    chochma: {"chips": []},
    bina: {"chips": []},
    chesed: {"chips": [{"c": ["#fff"], "title": "לבן", "t": "לבנה"}]},
    gevura: {"chips": [{"c": ["#c62828"], "title": "אדום", "t": "מאדים"}]},
    tiferet: {"chips": [{"c": ["#3faa5a"], "title": "ירוק", "t": "חמה"}]},
    netzach: {"chips": [{"kind": "nocol", "t": "\"כרובי עינא\" – נוגה"}]},
    hod: {"chips": [{"kind": "nocol", "t": "\"כרובי עינא\" – כוכב"}]},
    yesod: {"chips": [{"c": ["#26221c"], "title": "שחור", "t": "שבתאי"}]},
    malchut: {"chips": [{"c": ["#5b9bd5"], "title": "תכלת", "t": "צדק"}]}
  }},
  {id:"zohar", name:"הזוהר", ref:"קשת, נר, ציצית", href:"sefirot-colors.html#zohar-sec", col:"הזוהר", colRef:"קשת, נר, ציצית", colors:{
    keter: {"chips": []},
    chochma: {"chips": []},
    bina: {"chips": []},
    chesed: {"chips": [{"c": ["#fff"], "title": "לבן", "t": "\"חוור מימינא\""}]},
    gevura: {"chips": [{"c": ["#5b9bd5"], "title": "תכלת", "t": "\"תכלת משמאלא\" (ציצית)"}]},
    tiferet: {"chips": [{"c": ["#3faa5a"], "title": "ירוק", "t": "\"עמודא דאמצעיתא... ירוק\""}, {"c": ["#fff"], "title": "לבן", "t": "יה\"ו כולו – \"נהורא חוורא\""}]},
    netzach: {"chips": []},
    hod: {"chips": []},
    yesod: {"chips": [{"c": ["#fff", "#c62828", "#3faa5a"], "title": "לבן, אדום, ירוק", "t": "הקשת – \"חיור וסומק וירוק\""}]},
    malchut: {"chips": [{"c": ["#5b9bd5", "#26221c"], "title": "תכלת־שחור", "t": "\"נהורא תכלא אוכמא\", לזמנין סומקא"}, {"c": ["#5b9bd5"], "title": "תכלת", "t": "תכלת – כרסייא"}]}
  }},
  {id:"maarechet", name:"מערכת האלהות", ref:"פרקים ד, י\"ב", href:"sefirot-colors.html#maarechet", col:"מערכת האלהות", colRef:"פרקים ד, י\"ב", colors:{
    keter: {"chips": []},
    chochma: {"chips": []},
    bina: {"chips": [{"c": ["#3faa5a"], "title": "ירוק", "t": "\"קו ירוק\""}]},
    chesed: {"chips": [{"c": ["#fff"], "title": "לבן", "t": "\"כל דבר לבן\""}, {"c": ["#b9bec7"], "title": "כסף", "t": "כסף"}]},
    gevura: {"chips": [{"c": ["#d4a017"], "title": "זהב", "t": "\"דין זהב\""}]},
    tiferet: {"chips": [{"c": ["#fff"], "title": "לבן", "t": "\"אש לבנה\""}, {"c": ["#d9dde4"], "title": "לבן שאינו ככסף", "t": "ברזל, \"גם כן הוא נרמז לכסף כי רובו חסד\""}]},
    netzach: {"chips": []},
    hod: {"chips": []},
    yesod: {"chips": []},
    malchut: {"chips": [{"c": ["#5b9bd5"], "title": "תכלת", "t": "\"תכלת... כלולה בכל\""}, {"c": ["#b0305f"], "title": "תולעת שני", "t": "\"דין רפה\""}, {"c": ["#8b1e3f"], "title": "ארגמן, \"אדום יותר\"", "t": "ארגמן, \"שהוא אדום יותר\""}, {"c": ["#b87333"], "title": "נחושת", "t": "\"העטרה לנחשת, אדום אבל לא כזהב\""}, {"c": ["#26221c"], "title": "שחור", "t": "\"אש שחורה\""}]}
  }},
  {id:"gikatilla", name:"ר' יוסף ג'יקטילה", ref:"שערי אורה", href:"sefirot-colors.html#gikatilla", col:"ר' יוסף ג'יקטילה", colRef:"שערי אורה", colors:{
    keter: {"chips": [{"c": ["#fff"], "title": "לבן", "t": "\"בתכליתה לובן\""}]},
    chochma: {"chips": []},
    bina: {"chips": []},
    chesed: {"chips": []},
    gevura: {"chips": []},
    tiferet: {"chips": []},
    netzach: {"chips": []},
    hod: {"chips": []},
    yesod: {"chips": []},
    malchut: {"chips": [{"c": ["#26221c"], "title": "שחור", "t": "שד\"י – \"אש שחורה\""}, {"c": ["#c62828"], "title": "אדום", "t": "אלהי\"ם – \"אש אדומה\""}, {"c": ["#3faa5a"], "title": "ירוק", "t": "אדנ\"י – \"אש ירוקה\""}], "use": 2, "note": "הגוון לפי השם; בייחודים השם במלכות הוא אדנ\"י"}
  }},
  {id:"ramak", name:"הרמ\"ק", ref:"פרדס רמונים י; אור נערב ו", href:"sefirot-colors.html#ramak-sec", col:"הרמ\"ק", colRef:"פרדס רמונים י; אור נערב ו", colors:{
    keter: {"chips": [{"c": ["#fff"], "title": "לבן", "t": "\"לובן בתכלית\""}, {"c": ["#26221c"], "title": "שחור", "t": "שחור, כלפי המאציל"}, {"kind": "hidden", "title": "נעלם, בלי גוון", "t": "בלי גוון, בעצמו"}]},
    chochma: {"chips": [{"c": ["#5b9bd5"], "title": "תכלת", "t": "תכלת או ספיר, \"ראש לכל הגוונים\""}]},
    bina: {"chips": [{"c": ["#3faa5a"], "title": "ירוק", "t": "\"הירוק כעשבים\""}]},
    chesed: {"chips": [{"c": ["#b9bec7"], "title": "כסף", "t": "\"לבן קרוב אל התכלת... הכסף\""}, {"c": ["#fff"], "title": "לבן", "t": "\"יש שפי' בה הלובן סתם\"; \"ולפעמים יתייחס אליה הלובן ממש בגוון החלב\""}]},
    gevura: {"chips": [{"c": ["#c62828"], "title": "אדום", "t": "אודם"}, {"c": ["#26221c"], "title": "שחור", "t": "שחור"}, {"c": ["#5b9bd5"], "title": "תכלת", "t": "תכלת"}, {"c": ["#d4a017"], "title": "זהב", "t": "זהב"}]},
    tiferet: {"chips": [{"c": ["#fff", "#c62828"], "title": "לבן ואדום", "t": "לבן ואדום"}, {"c": ["#f2c94c", "#3faa5a"], "title": "ירוק כחלמון, צהבהב", "t": "\"ירוק כחלמון ביצה\""}, {"c": ["#7e3fa6"], "title": "ארגמן", "t": "ארגמן"}]},
    netzach: {"chips": [{"c": ["#c62828", "#fff"], "split": 35, "title": "אדום נוטה ללבן", "t": "\"אודם נוטה אל הלובן\""}]},
    hod: {"chips": [{"c": ["#fff", "#c62828"], "split": 35, "title": "לבן נוטה לאדום", "t": "\"לובן נוטה אל האודם\""}]},
    yesod: {"chips": [{"c": ["#fff", "#c62828"], "title": "לבן ואדום", "t": "\"גוון תערובת\""}, {"kind": "all", "title": "כלול מכל גוון", "t": "כלול מכל"}]},
    malchut: {"chips": [{"kind": "all", "title": "כלול מכל גוון", "t": "כלולה מכל גוון"}, {"c": ["#5b9bd5"], "title": "תכלת", "t": "תכלת"}, {"c": ["#fff"], "title": "לבן", "t": "\"הגוון עצמי... לבן המאיר\""}, {"c": ["#3faa5a"], "title": "ירוק", "t": "\"התכלת מתהפך אל ירוק ככרתי\", בעלות השחר"}, {"c": ["#26221c"], "title": "שחור", "t": "\"מייחס השחרות למדה זו להעדר אורה\", בימי חסרונה"}]}
  }},
  {id:"tidhar", name:"עץ התדהר", ref:"בן זמננו, תשפ\"ב–תשפ\"ג", href:"sefirot-colors.html#tidhar", col:"עץ התדהר", colRef:"עמ' קעב–קעו וכרטיסים", modern:true,
   /* הצבעים לפי ערכי ה־RGB שבספר עצמו ("יצוג צבעי האור על מסכים"), עמודים קעב–קעג */
   extra:{daat:{chips:[{"c":["#7f00ff"], "title":"סגול", "t":"\"דעת/סגול ?\"; \"לגבי צבע של ספירת הדעת עדיין לא מצאתי מקור\""}]}},
   colors:{
    keter: {"chips": [{"c": ["#ffffff"], "title": "לבן", "t": "\"מצד השפעתו בספירות צבעו לבן\""}, {"kind": "nocol", "t": "בכרטיס: \"גלגלתא כתר לבן/שקוף\""}]},
    chochma: {"chips": [{"c": ["#007fff"], "title": "תכלת", "t": "תכלת; בכרטיס: \"כחול שמים\""}]},
    bina: {"chips": [{"c": ["#ffb000"], "title": "זהב", "t": "זהב"}]},
    chesed: {"chips": [{"c": ["#00ffff"], "title": "תכלת מלובן", "t": "\"תכלת מלובן\""}]},
    gevura: {"chips": [{"c": ["#ff0000"], "title": "אדום", "t": "אדום"}]},
    tiferet: {"chips": [{"c": ["#ffff00"], "title": "צהוב", "t": "\"צהוב חלמון ביצה\"; בכרטיס: \"צהוב כורכום\""}]},
    netzach: {"chips": [{"c": ["#00ff00"], "title": "ירוק", "t": "\"ירוק הנוטה לכחול\""}]},
    hod: {"chips": [{"c": ["#880000"], "title": "אדום כהה", "t": "\"אדום כהה נוטה לשחור\"; בכרטיס: \"אדום שני\""}]},
    yesod: {"chips": [{"c": ["#b3ff00"], "title": "ירוק נוטה לצהוב", "t": "\"ירוק הנוטה לצהוב\""}]},
    malchut: {"chips": [{"c": ["#610061"], "title": "ארגמן", "t": "\"ארגמן סגול כעין יין צלול\""}, {"c": ["#4c1c24"], "title": "בורדו", "t": "\"ארגמן אדום כעין בורדו\", כשאורה \"נמשך לבריאה\""}]}
  }}
];
var DATA = {
  sefirot: [{id:'keter',he:'כתר'},{id:'chochma',he:'חכמה'},{id:'bina',he:'בינה'},{id:'chesed',he:'חסד'},{id:'gevura',he:'גבורה'},{id:'tiferet',he:'תפארת'},{id:'netzach',he:'נצח'},{id:'hod',he:'הוד'},{id:'yesod',he:'יסוד'},{id:'malchut',he:'מלכות'}],
  names: {'אהי"ה':'keter','י"ה':'chochma','אלקים חיים':'bina','אל':'chesed','אלקים':'gevura','הוי"ה':'tiferet',"ה' צבאות":'netzach','אלקים צבאות':'hod','אל חי':'yesod','אדנ"י':'malchut'},
  methods: METHODS
};

/* ---- הכנה: הגוון שצובע את השמות בכל ספירה ---- */
function prep(e){
    var ch = e.chips || [];
    if(!ch.length){ e.kind = 'none'; e.t = ''; return; }
    var u = (e.use != null) ? e.use : -1;
    if(u < 0){ for(var i=0;i<ch.length;i++){ if(ch[i].kind !== 'nocol'){ u = i; break; } } }
    if(u < 0) u = 0;
    var p = ch[u];
    if(p.c) e.c = p.c; if(p.kind) e.kind = p.kind; if(p.split) e.split = p.split;
    if(!e.t) e.t = p.t;
    var alt = ch.filter(function(x,i){ return i !== u; }).map(function(x){ return x.t; });
    if(alt.length) e.alt = alt;
}
METHODS.forEach(function(m){
  Object.keys(m.colors).forEach(function(f){ prep(m.colors[f]); });
  if(m.extra) Object.keys(m.extra).forEach(function(f){ prep(m.extra[f]); });   /* ספירות נוספות, כמו דעת */
});

var RAINBOW = ['#fff','#5b9bd5','#3faa5a','#f2c94c','#c62828','#7e3fa6'];
function hex6(h){h=h.replace('#','');if(h.length===3)h=h.split('').map(function(x){return x+x}).join('');return h;}
function lum(h){h=hex6(h);var r=parseInt(h.substr(0,2),16)/255,g=parseInt(h.substr(2,2),16)/255,b=parseInt(h.substr(4,2),16)/255;return .2126*r+.7152*g+.0722*b;}
function isWhite(c){ return hex6(c).toLowerCase()==='ffffff'; }
function stops(cs,split,dir){
  if(cs.length===2&&split) return 'linear-gradient('+dir+','+cs[0]+' '+split+'%,'+cs[1]+' '+split+'%)';
  var n=cs.length,p=[];cs.forEach(function(c,i){p.push(c+' '+Math.round(i*100/n)+'%',c+' '+Math.round((i+1)*100/n)+'%');});
  return 'linear-gradient('+dir+','+p.join(',')+')';}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;').replace(/'/g,'&#x27;');}

/* רקע CSS לגוון (לדוגמיות, נקודות וכו') */
function bg(e){
  var k=e.kind||'';
  if(k==='glow') return 'radial-gradient(#fff,#eee8da)';
  if(k==='all') return 'conic-gradient('+RAINBOW.concat(['#fff']).join(',')+')';
  if(k==='hidden'||k==='nocol'||k==='none') return 'transparent';
  var cs=e.c;
  if(cs.length===1) return cs[0];
  if(cs.length===3) return 'conic-gradient('+cs[0]+' 0 33%,'+cs[1]+' 0 66%,'+cs[2]+' 0)';
  return 'linear-gradient(135deg,'+cs[0]+' '+(e.split||50)+'%,'+cs[1]+' '+(e.split||50)+'%)';}
/* נקודה עגולה, בסגנון של טבלת ההשוואה */
function dot(e){
  var k=e.kind||'';
  if(k==='glow') return 'background:radial-gradient(#fff,#eee8da);border-style:dashed';
  if(k==='ring') return 'background:'+e.c[0]+';box-shadow:0 0 0 2px #fdd835,0 0 0 4px #e53935';
  if(k==='hidden'||k==='nocol') return 'background:transparent;border-style:dashed;border-color:#9c7a33';
  if(k==='none') return 'background:transparent;border-style:dashed;border-color:#c9bda5';
  var b='background:'+bg(e);
  if(e.c&&e.c.length===1&&isWhite(e.c[0])) b+=';border-color:#cbbd9c';
  return b;}
/* דוגמית עם מסגרת משלה (לשימוש מחוץ לטבלה) */
function swatch(e){
  var k=e.kind||'';
  if(k==='none') return 'background:#f4f0e6;border:1px dashed #c9bda5';
  if(k==='nocol'||k==='hidden') return 'background:transparent;border:1px dashed #9c7a33';
  if(k==='glow') return 'background:radial-gradient(#fff,#eee8da);border:1px dashed #cbbd9c';
  if(k==='ring') return 'background:'+e.c[0]+';box-shadow:0 0 0 2px #fdd835,0 0 0 4px #e53935';
  var light=k!=='all'&&e.c.every(function(c){return lum(c)>.8});
  return 'background:'+bg(e)+';border:1px solid '+(light?'#cbbd9c':'#0003');}
/* CSS לאותיות שם בגוון הספירה */
function letterCss(e){
  var k=e.kind||'';
  if(k==='none'||k==='nocol') return 'color:#b3a994;background:none;-webkit-text-stroke:0;text-shadow:none;filter:none';
  if(k==='hidden') return 'color:transparent;background:none;-webkit-text-stroke:1px #9c7a33;text-shadow:none;filter:none;opacity:.85';
  if(k==='glow') return 'color:#fffdf5;background:none;-webkit-text-stroke:1.1px #b39a5e;text-shadow:0 0 14px #fff3cc,0 0 3px #efe3c2;filter:none';
  var cs=k==='all'?RAINBOW:e.c, light=cs.every(function(c){return lum(c)>.8});
  var stroke=light?'-webkit-text-stroke:1px #b39a5e;':'-webkit-text-stroke:.6px #4a2d0f55;';
  if(cs.length===1) return 'color:'+cs[0]+';background:none;'+stroke+'text-shadow:none;filter:none';
  var sp=(cs.length===2&&!e.split)?52:e.split;
  return 'background:'+stops(cs,sp,'180deg')+';-webkit-background-clip:text;background-clip:text;color:transparent;'+stroke+'text-shadow:none;filter:none';}
/* CSS לשם בתוך הטקסט (גלולה בגוון הספירה) */
function pillCss(e){
  var k=e.kind||'';
  if(k==='none'||k==='nocol') return 'background:#ece5d6;color:#8a7f6d;border:1px dashed #c9bda5;text-shadow:none';
  if(k==='hidden') return 'background:transparent;color:#6f665a;border:1px dashed #9c7a33;text-shadow:none';
  if(k==='glow') return 'background:radial-gradient(#fff,#f1ebdc);color:#5c4a2a;border:1px dashed #cbbd9c;text-shadow:none';
  var cs=k==='all'?RAINBOW:e.c;
  var b=k==='all'?bg(e):cs.length===1?cs[0]:stops(cs,e.split||50,'135deg');
  var avg=cs.reduce(function(a,c){return a+lum(c)},0)/cs.length;
  var fg=avg>.62?'color:#3a2e1d;text-shadow:0 0 2px #fff,0 0 2px #fff':'color:#fff;text-shadow:0 0 2px #1d1408,0 0 2px #1d1408,0 0 4px #1d1408';
  return 'background:'+b+';'+fg+';'+(avg>.8?'border:1px solid #c9bda5':'border:1px solid transparent');}

function method(id){for(var i=0;i<METHODS.length;i++) if(METHODS[i].id===id) return METHODS[i]; return METHODS[0];}
function entry(f,mid){ var m=method(mid||'shir'); return m.colors[f] || (m.extra && m.extra[f]); }

/* ---- צביעת דף: כל אלמנט עם data-sef="<ספירה>" (ואם רוצים data-sef-m="<שיטה>") ----
 * HTML: מקבל רקע (data-sef-as="bg") או נקודה בסגנון הטבלה (data-sef-as="dot", ברירת המחדל).
 * SVG: gradient מקבל את צבעי ה־stop; צורה מקבלת fill (צבע אחד, או gradient שנוצר כאן). */
var NS='http://www.w3.org/2000/svg', defs=null;
function svgFill(e,mid,f){
  var k=e.kind||'';
  if(k==='glow') return '#fffdf5';
  if(k==='hidden'||k==='none'||k==='nocol') return 'none';
  var cs=k==='all'?RAINBOW:e.c;
  if(cs.length===1) return cs[0];
  var id='sefg-'+mid+'-'+f;
  if(!document.getElementById(id)){
    if(!defs){ var sv=document.createElementNS(NS,'svg'); sv.setAttribute('width','0'); sv.setAttribute('height','0'); sv.setAttribute('aria-hidden','true'); sv.style.position='absolute';
      defs=document.createElementNS(NS,'defs'); sv.appendChild(defs); document.body.appendChild(sv); }
    var g=document.createElementNS(NS,'linearGradient'); g.id=id; g.setAttribute('x1','0');g.setAttribute('y1','0');g.setAttribute('x2','1');g.setAttribute('y2','1');
    var n=cs.length, sp=(n===2&&e.split)?e.split/100:null;
    cs.forEach(function(c,i){
      var a=sp!=null?(i===0?0:sp):i/n, b=sp!=null?(i===0?sp:1):(i+1)/n;
      [a,b].forEach(function(o){var s=document.createElementNS(NS,'stop'); s.setAttribute('offset',String(o)); s.setAttribute('stop-color',c); g.appendChild(s);});
    });
    defs.appendChild(g);
  }
  return 'url(#'+id+')';}
/* רשימת דוגמיות לשיטה שלמה: <ul data-sef-list="<שיטה>"> נמלא בעשר הספירות, הצבע ולשון המקור */
function listHtml(mid){
  return DATA.sefirot.map(function(s){
    var e=entry(s.id,mid);
    return '<li><span class="sw" style="'+dot(e)+'"></span><span><b>'+esc(s.he)+'</b>: '+(e.kind==='none'?'—':esc(e.t))+(e.alt?' <small>(וגם: '+esc(e.alt.join('; '))+')</small>':'')+'</span></li>';
  }).join('');}
function paint(root){
  root=root||document;
  Array.prototype.forEach.call(root.querySelectorAll('[data-sef-list]'), function(ul){ ul.innerHTML=listHtml(ul.getAttribute('data-sef-list')); });
  Array.prototype.forEach.call(root.querySelectorAll('[data-sef]'), function(el){
    var f=el.getAttribute('data-sef'), mid=el.getAttribute('data-sef-m')||'shir', e=entry(f,mid); if(!e) return;
    if(el.namespaceURI===NS){
      var tag=el.tagName.toLowerCase();
      if(tag==='lineargradient'||tag==='radialgradient'){
        var st=el.querySelectorAll('stop'), cs=e.kind==='glow'?['#fff','#eee8da']:(e.c||[]);
        if(!cs.length) return;
        if(st.length===cs.length){ Array.prototype.forEach.call(st,function(s,i){ s.setAttribute('stop-color',cs[i]); }); }
        else { st[0].setAttribute('stop-color',cs[0]); st[st.length-1].setAttribute('stop-color',cs[cs.length-1]); }
      } else el.setAttribute('fill', svgFill(e,mid,f));
      return;
    }
    var as=el.getAttribute('data-sef-as')||'dot';
    if(as==='bg') el.style.background=bg(e);
    else el.setAttribute('style', (as==='swatch'?swatch(e):dot(e)));
  });
}

/* ---- טבלת ההשוואה (sefirot-colors.html#compare) ---- */
function chipHtml(c){
  if(c.kind==='nocol') return '<span class="ch nocol">'+esc(c.t)+'</span>';
  return '<span class="ch"><i class="dot" style="'+dot(c)+'"'+(c.title?' title="'+esc(c.title)+'"':'')+'></i>'+esc(c.t)+'</span>';}
function compareHtml(){
  var h='<table class="cmp"><tr><th class="sticky">ספירה</th>';
  METHODS.forEach(function(m){
    if(m.ours) h+='<th class="ours">'+esc(m.col)+'<small>'+esc(m.colRef)+'</small></th>';
    else h+='<th><a href="'+esc(m.href.replace(/^sefirot-colors\.html/,''))+'">'+esc(m.col)+'</a><small>'+esc(m.colRef)+'</small></th>';
  });
  h+='</tr>';
  DATA.sefirot.forEach(function(s){
    var ours=METHODS[0].colors[s.id].chips[0];
    h+='<tr><th class="sticky" scope="row"><span class="sefn"><i class="dot" style="'+dot(ours)+'"></i>'+esc(s.he)+'</span></th>';
    METHODS.forEach(function(m){
      var ch=m.colors[s.id].chips;
      if(!ch.length) h+='<td class="empty">—</td>';
      else h+='<td'+(m.ours?' class="ours"':'')+'>'+ch.map(chipHtml).join('')+'</td>';
    });
    h+='</tr>';
  });
  return h+'</table>';}

window.SEFIROT = {data:DATA, method:method, entry:entry, bg:bg, dot:dot, swatch:swatch, letterCss:letterCss, pillCss:pillCss,
  paint:paint, compareHtml:compareHtml, listHtml:listHtml,
  label:function(e){return e.kind==='none'?'המקור אינו אומר דבר על ספירה זו':e.t+(e.alt?' · '+e.alt.join(' · '):'');}};
if(typeof document!=='undefined'){
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',function(){paint();}); else paint();
}
})();
