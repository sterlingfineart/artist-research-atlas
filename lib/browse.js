'use strict';
/*
 * Browse: find artists by century, country, movement or role, through live
 * Wikidata queries — one facet at a time, or several combined with a GO
 * button (century + country + movement + medium, ANDed). The result is a
 * finding aid only — each artist links into the existing report flow, where
 * works are linked to the holding institution's verified page. Every
 * curated QID was verified against Wikidata (2026-11-16); no identifier
 * here is guessed. Counts of eligible artists per movement were checked
 * the same day (8–703 each).
 *
 * Query shape (two steps, both live): (1) rank the best-documented artists
 * for the filters by sitelinks; (2) fetch their details. Occupation
 * eligibility is the same as search — P106 a subclass of one of the five
 * roots — but the subclass closure is resolved once (a cheap query, cached
 * in-process) and passed as VALUES: the P279* join inside the ranking
 * query times out on Wikidata (tested 2026-11-16), while the VALUES form
 * answers in ~15s for the heaviest facet (19th century).
 *
 * Country is by citizenship (P27), modern country plus the historical
 * states whose artists belong under it: citizenship in Wikidata records
 * the polity of the time — Rembrandt and Vermeer are "Dutch Republic",
 * Van Gogh and Mondrian "Kingdom of the Netherlands", Leonardo
 * "Republic of Florence" — so a modern-country P27 query returns no
 * Dutch masters at all and misses the whole Italian Renaissance. The
 * country query therefore matches P27 against a curated polity list
 * (verified QIDs, see COUNTRIES) with the P279* occupation join: that
 * form answers in ~18–30s for the big countries and finds the masters,
 * where the VALUES occupation form times out for the Kingdom of the
 * Netherlands at every threshold. Birthplace was tried first and ruled
 * out — both the P131* chain and the birthplace-country (P17) forms time
 * out on Wikidata for every country tested.
 *
 * The country list itself is dynamic (getCountryFacets): a live COUNT of
 * every distinct P27 value among eligible artists (937 polities, 294,776
 * artists, counted 2026-11-16), grouped under the modern country from
 * COUNTRIES, with any polity not in the table appearing under its own
 * label — so no country is ever omitted. P17 is NOT used for grouping:
 * it does not map historical polities to modern countries (Dutch Republic
 * -> itself, Republic of Florence -> itself, Bavaria -> no P17, Travancore
 * -> British Raj AND Dominion of India). The count query takes ~12s and
 * is cached in-process; if it fails, the static 183-country table is
 * returned instead, so the page still works.
 */
const { sparqlWD, getJSON, qs, v, qid, safe, wdYear } = require('./util');
const { ROOTS } = require('./search');

const LANGS = 'en,mul';
const ROOT_VALUES = Object.keys(ROOTS).map((k) => 'wd:' + k).join(' ');

const CENTURIES = [12, 13, 14, 15, 16, 17, 18, 19, 20];
const centuryLabel = (c) => {
  const suffix = c % 10 === 1 && c % 100 !== 11 ? 'st' : c % 10 === 2 && c % 100 !== 12 ? 'nd' : c % 10 === 3 && c % 100 !== 13 ? 'rd' : 'th';
  return `${c}${suffix} century`;
};

// Countries of citizenship (Wikidata QIDs), generated 2026-11-16 from a live
// count of every distinct P27 value among eligible artists (937 polities,
// 294,776 artists). The value is the modern country's QID; the polity list
// adds the historical states whose artists belong under it — citizenship in
// Wikidata records the polity of the time, so without them the Dutch
// masters (Dutch Republic) and the whole Italian Renaissance (Republic of
// Florence, Papal States, ...) would be missing. Every polity found is in
// this table or appears under its own label (see getCountryFacets), so no
// country is ever omitted. Judgement calls, checked against real artists'
// records and the polities' own descriptions: the Holy Roman Empire sits
// under Germany AND Italy; Denmark-Norway and the Union of Sweden and
// Norway under both their countries; Austria-Hungary under Austria AND
// Hungary; the Soviet Union, Russian Empire and Tsardom under Russia (the
// earlier single-country precedent); Yugoslavia and its federations under
// Serbia (capital Belgrade); Czechoslovakia under the Czech Republic
// (capital Prague); the United Arab Republic under Egypt AND Syria; the
// Burgundian Netherlands under Belgium AND the Netherlands; the United
// Kingdom of the Netherlands under the Netherlands AND Belgium; Schleswig
// under Germany AND Denmark (now divided between them). Dynasties map to
// the modern country they ruled (Song/Ming/Qing/Tang/Yuan to China, Joseon
// and Goryeo to South Korea, Mughal/British Raj to India). A few P27 values
// are not countries at all and stay under their own label: Hong Kong,
// Korea (the whole peninsula), Africa, statelessness, the Low Countries,
// the British Empire, French Indochina, and Indigenous nations (Cherokee,
// Navajo, Choctaw, Great Sioux, Potawatomi, Meskwaki, Five Nations). The
// same rule covers citizenships recorded as a town, city or people rather
// than a polity: they stand on their own instead of being folded under a
// country — a town is not a country, and folding one in put Julius Evola,
// whose citizenship Wikidata records as Apodaca (a town in Mexico), under
// Mexico (2026-11-16). Cities (New York City, Barcelona, Bologna, Bergamo,
// Fort-de-France, Nördlingen), the Hanseatic City of Lübeck, peoples
// (Abenaki, Nuu-chah-nulth, Six Nations, Bretons, Innu), the Falisci and
// the Congolese were all removed from the country lists for this reason;
// three were kept deliberately — Flanders (a region, under Belgium),
// Jacksonville (no English label, so it cannot stand alone, under the
// United States) and Palestine, Texas (its label collides with the country
// Palestine, under the United States).
const COUNTRIES = [
  ["Afghanistan", "Q889", ["Q889"]],
  ["Albania", "Q222", ["Q222"]],
  ["Algeria", "Q262", ["Q262"]],
  ["Andorra", "Q228", ["Q228"]],
  ["Angola", "Q916", ["Q916"]],
  ["Antigua and Barbuda", "Q781", ["Q781"]],
  ["Argentina", "Q414", ["Q414"]],
  ["Armenia", "Q399", ["Q399", "Q132856", "Q139670"]],
  ["Australia", "Q408", ["Q408", "Q1780114", "Q3224", "Q1083009", "Q5148519", "Q56850459"]],
  ["Austria", "Q40", ["Q40", "Q28513", "Q131964", "Q533534", "Q153136", "Q699964", "Q16543832", "Q701614", "Q116896904", "Q3113481"]],
  ["Azerbaijan", "Q227", ["Q227", "Q206411", "Q131083"]],
  ["Bahrain", "Q398", ["Q398"]],
  ["Bangladesh", "Q902", ["Q902"]],
  ["Barbados", "Q244", ["Q244"]],
  ["Belarus", "Q184", ["Q184", "Q2895", "Q842199"]],
  ["Belgium", "Q31", ["Q31", "Q1031430", "Q6581823", "Q622783", "Q158835", "Q15864", "Q700283", "Q234", "Q157070", "Q157109", "Q159856"]],
  ["Belize", "Q242", ["Q242"]],
  ["Benin", "Q962", ["Q962"]],
  ["Bhutan", "Q917", ["Q917"]],
  ["Bolivia", "Q750", ["Q750"]],
  ["Bosnia and Herzegovina", "Q225", ["Q225"]],
  ["Botswana", "Q963", ["Q963"]],
  ["Brazil", "Q155", ["Q155", "Q2088324", "Q217230"]],
  ["Bulgaria", "Q219", ["Q219", "Q121932", "Q147909", "Q815731", "Q459780"]],
  ["Burkina Faso", "Q965", ["Q965"]],
  ["Burundi", "Q967", ["Q967"]],
  ["Cambodia", "Q424", ["Q424"]],
  ["Cameroon", "Q1009", ["Q1009"]],
  ["Canada", "Q16", ["Q16", "Q1134180", "Q1121436", "Q2569593", "Q1973", "Q2935756"]],
  ["Cape Verde", "Q1011", ["Q1011"]],
  ["Central African Republic", "Q929", ["Q929"]],
  ["Chad", "Q657", ["Q657"]],
  ["Chile", "Q298", ["Q298"]],
  ["Colombia", "Q739", ["Q739", "Q1061488"]],
  ["Comoros", "Q970", ["Q970"]],
  ["Cook Islands", "Q26988", ["Q26988"]],
  ["Costa Rica", "Q800", ["Q800"]],
  ["Croatia", "Q224", ["Q224", "Q153128", "Q208169", "Q533558", "Q698248", "Q528042"]],
  ["Cuba", "Q241", ["Q241"]],
  ["Cyprus", "Q229", ["Q229", "Q15240466"]],
  ["Czech Republic", "Q213", ["Q213", "Q33946", "Q42585", "Q39193", "Q140359", "Q152750", "Q853348", "Q43266", "Q2010024", "Q2670751"]],
  ["Democratic Republic of the Congo", "Q974", ["Q974"]],
  ["Denmark", "Q35", ["Q35", "Q756617", "Q62651"]],
  ["Dominica", "Q784", ["Q784"]],
  ["Dominican Republic", "Q786", ["Q786"]],
  ["Ecuador", "Q736", ["Q736"]],
  ["Egypt", "Q79", ["Q79", "Q170468", "Q124943", "Q3087763", "Q11768", "Q370173", "Q127861", "Q282428", "Q191324"]],
  ["El Salvador", "Q792", ["Q792"]],
  ["Equatorial Guinea", "Q983", ["Q983"]],
  ["Eritrea", "Q986", ["Q986"]],
  ["Estonia", "Q191", ["Q191"]],
  ["Ethiopia", "Q115", ["Q115", "Q207521"]],
  ["Finland", "Q33", ["Q33", "Q62633"]],
  ["France", "Q142", ["Q142", "Q70972", "Q71084", "Q155019", "Q1876237", "Q70802", "Q706553", "Q4712", "Q642314", "Q15878", "Q69323", "Q71092", "Q252157", "Q646374", "Q10828323", "Q17070", "Q210682", "Q271894", "Q1122980", "Q3456410"]],
  ["Gabon", "Q1000", ["Q1000"]],
  ["Georgia", "Q230", ["Q230", "Q130229", "Q245160", "Q2029317"]],
  ["Germany", "Q183", ["Q183", "Q1206012", "Q16957", "Q27306", "Q43287", "Q154195", "Q12548", "Q153015", "Q159631", "Q41304", "Q186320", "Q7318", "Q161036", "Q164079", "Q2227570", "Q20135", "Q1055", "Q713750", "Q155570", "Q156199", "Q326029", "Q980", "Q158445", "Q151624", "Q256961", "Q704300", "Q529605", "Q1202", "Q38872", "Q569871", "Q150981", "Q704288", "Q706018", "Q22880", "Q157710", "Q16550783", "Q3462133", "Q2843", "Q168651", "Q284667", "Q693669", "Q161215", "Q836680", "Q24879", "Q47261", "Q159626", "Q153943", "Q675127", "Q26167", "Q117020", "Q278874", "Q1794", "Q34762", "Q156111", "Q165763", "Q556263", "Q44352", "Q173863", "Q2372248", "Q694231", "Q1998459", "Q11812551", "Q2090", "Q148499", "Q259511", "Q264970", "Q637238", "Q641138", "Q675085", "Q682318", "Q704312", "Q705438", "Q873634", "Q13427044", "Q20011161", "Q118177298", "Q1194", "Q1209", "Q155578", "Q157367", "Q323167", "Q693551", "Q693911", "Q836937", "Q14164803", "Q14551680", "Q4178", "Q55300", "Q55304", "Q55306", "Q109057", "Q151095", "Q156031", "Q319250", "Q552033", "Q616804", "Q648297", "Q650370", "Q660702", "Q673865", "Q686965", "Q690821", "Q697685", "Q1454724", "Q1541716", "Q1541723", "Q1794352", "Q1900716", "Q3624762", "Q5499881", "Q7904317", "Q17540123", "Q18450904"]],
  ["Ghana", "Q117", ["Q117"]],
  ["Greece", "Q41", ["Q41", "Q844930", "Q209065", "Q1363688", "Q5690", "Q11225429", "Q13533316", "Q13533353", "Q57394139", "Q368628", "Q20379949", "Q17765809", "Q156882", "Q187570", "Q191082", "Q833665", "Q871792", "Q1231539", "Q1412043", "Q1443132", "Q2288441", "Q2338980", "Q2857905", "Q11953081", "Q16562724", "Q21083662", "Q42307600"]],
  ["Grenada", "Q769", ["Q769"]],
  ["Guatemala", "Q774", ["Q774", "Q9063401"]],
  ["Guinea", "Q1006", ["Q1006"]],
  ["Guinea-Bissau", "Q1007", ["Q1007"]],
  ["Guyana", "Q734", ["Q734"]],
  ["Haiti", "Q790", ["Q790"]],
  ["Honduras", "Q783", ["Q783"]],
  ["Hong Kong", "Q8646", ["Q1054923"]],
  ["Hungary", "Q28", ["Q28", "Q28513", "Q171150", "Q253094", "Q600018"]],
  ["Iceland", "Q189", ["Q189"]],
  ["India", "Q668", ["Q668", "Q129286", "Q1775277", "Q33296", "Q17319155", "Q859966", "Q18129046", "Q1060520", "Q1785349", "Q6416549", "Q2376315", "Q3192661", "Q11916911", "Q150058", "Q4997536", "Q6124144", "Q6207845", "Q6748050", "Q7530545"]],
  ["Indonesia", "Q252", ["Q252", "Q188161"]],
  ["Iran", "Q794", ["Q794", "Q18234383", "Q107258515", "Q63158027", "Q207991", "Q3746183", "Q178084", "Q3112669", "Q63149558", "Q170568"]],
  ["Iraq", "Q796", ["Q796", "Q149805", "Q3041595", "Q3108185", "Q132690253"]],
  ["Ireland", "Q27", ["Q27", "Q215530", "Q31747", "Q57695350"]],
  ["Israel", "Q801", ["Q801", "Q23792", "Q407199"]],
  ["Italy", "Q38", ["Q38", "Q172579", "Q4948", "Q12548", "Q170174", "Q154849", "Q173065", "Q174306", "Q153529", "Q148540", "Q209857", "Q1747689", "Q180393", "Q2577303", "Q391980", "Q188586", "Q165154", "Q2252973", "Q223936", "Q64576860", "Q252580", "Q426025", "Q838931", "Q736727", "Q165040", "Q55599391", "Q213353", "Q649202", "Q723118", "Q659312", "Q1231403", "Q329967", "Q766501", "Q641", "Q1210", "Q1243", "Q1460", "Q2044", "Q206730", "Q693570", "Q729481", "Q933592", "Q1072140", "Q3845763", "Q4420718", "Q16595757", "Q1216", "Q15124", "Q16139", "Q207989", "Q2268597", "Q13496558", "Q25934646", "Q1256", "Q1273", "Q1447", "Q681348", "Q958521", "Q1568583", "Q1867844", "Q2037576", "Q3136685", "Q3429952", "Q3968612"]],
  ["Ivory Coast", "Q1008", ["Q1008"]],
  ["Jamaica", "Q766", ["Q766"]],
  ["Japan", "Q17", ["Q17", "Q188712", "Q205662", "Q28025", "Q736839"]],
  ["Jordan", "Q810", ["Q810"]],
  ["Kazakhstan", "Q232", ["Q232"]],
  ["Kenya", "Q114", ["Q114"]],
  ["Kosovo", "Q1246", ["Q1246"]],
  ["Kuwait", "Q817", ["Q817"]],
  ["Kyrgyzstan", "Q813", ["Q813"]],
  ["Laos", "Q819", ["Q819"]],
  ["Latvia", "Q211", ["Q211"]],
  ["Lebanon", "Q822", ["Q822", "Q130842", "Q139708", "Q108865226", "Q108865218"]],
  ["Liberia", "Q1014", ["Q1014"]],
  ["Libya", "Q1016", ["Q1016", "Q192435", "Q284568", "Q4843701"]],
  ["Liechtenstein", "Q347", ["Q347"]],
  ["Lithuania", "Q37", ["Q37", "Q49683", "Q523380", "Q8272919"]],
  ["Luxembourg", "Q32", ["Q32", "Q2719360"]],
  ["Madagascar", "Q1019", ["Q1019"]],
  ["Malawi", "Q1020", ["Q1020"]],
  ["Malaysia", "Q833", ["Q833"]],
  ["Mali", "Q912", ["Q912"]],
  ["Malta", "Q233", ["Q233", "Q6744657", "Q7603765", "Q3355522"]],
  ["Mauritania", "Q1025", ["Q1025"]],
  ["Mauritius", "Q1027", ["Q1027"]],
  ["Mexico", "Q96", ["Q96", "Q170603", "Q82112", "Q60176"]],
  ["Moldova", "Q217", ["Q217"]],
  ["Monaco", "Q235", ["Q235"]],
  ["Mongolia", "Q711", ["Q711", "Q212056"]],
  ["Montenegro", "Q236", ["Q236", "Q386496"]],
  ["Morocco", "Q1028", ["Q1028"]],
  ["Mozambique", "Q1029", ["Q1029"]],
  ["Myanmar", "Q836", ["Q836"]],
  ["Namibia", "Q1030", ["Q1030"]],
  ["Nepal", "Q837", ["Q837"]],
  ["Netherlands", "Q55", ["Q55", "Q29999", "Q170072", "Q27996474", "Q15864", "Q157109", "Q188553", "Q3292403", "Q212278", "Q330533", "Q762943", "Q102911", "Q774783", "Q25227", "Q707767", "Q25396", "Q2118709"]],
  ["New Zealand", "Q664", ["Q664", "Q5148518"]],
  ["Nicaragua", "Q811", ["Q811"]],
  ["Niger", "Q1032", ["Q1032"]],
  ["Nigeria", "Q1033", ["Q1033", "Q682777"]],
  ["Niue", "Q34020", ["Q34020"]],
  ["North Korea", "Q423", ["Q423"]],
  ["North Macedonia", "Q221", ["Q221"]],
  ["Northern Cyprus", "Q23681", ["Q23681"]],
  ["Norway", "Q20", ["Q20", "Q62651", "Q62589"]],
  ["Oman", "Q842", ["Q842"]],
  ["Pakistan", "Q843", ["Q843"]],
  ["Palestine", "Q219060", ["Q219060", "Q193714"]],
  ["Panama", "Q804", ["Q804"]],
  ["Papua New Guinea", "Q691", ["Q691"]],
  ["Paraguay", "Q733", ["Q733"]],
  ["People's Republic of China", "Q148", ["Q148", "Q7462", "Q8733", "Q9903", "Q13426199", "Q7313", "Q9683", "Q29520", "Q319460", "Q1147043", "Q12060881", "Q1326742", "Q7405", "Q391189", "Q17252", "Q4958", "Q2308761", "Q7209", "Q875305", "Q1147037", "Q1730130"]],
  ["Peru", "Q419", ["Q419", "Q211435"]],
  ["Philippines", "Q928", ["Q928", "Q6042084", "Q31351948"]],
  ["Poland", "Q36", ["Q36", "Q207272", "Q172107", "Q221457", "Q211274", "Q152115", "Q501303", "Q1649871", "Q216173", "Q81720", "Q1792", "Q568638", "Q570702", "Q691981", "Q11750128"]],
  ["Portugal", "Q45", ["Q45", "Q45670", "Q323904"]],
  ["Qatar", "Q846", ["Q846"]],
  ["Republic of the Congo", "Q971", ["Q971"]],
  ["Romania", "Q218", ["Q218", "Q203493", "Q389004", "Q958291", "Q842794", "Q10957559", "Q2685298"]],
  ["Russia", "Q159", ["Q159", "Q15180", "Q34266", "Q2305208", "Q2184", "Q139319", "Q186096", "Q170770", "Q131337", "Q5481", "Q5710", "Q168811", "Q16746854", "Q130276", "Q173761", "Q746558", "Q2381337", "Q960", "Q75903", "Q199711", "Q491106", "Q964024", "Q1419584"]],
  ["Rwanda", "Q1037", ["Q1037"]],
  ["Saint Lucia", "Q760", ["Q760"]],
  ["Samoa", "Q683", ["Q683"]],
  ["San Marino", "Q238", ["Q238"]],
  ["Saudi Arabia", "Q851", ["Q851"]],
  ["Senegal", "Q1041", ["Q1041"]],
  ["Serbia", "Q403", ["Q403", "Q83286", "Q191077", "Q15102440", "Q36704", "Q1290149", "Q241748", "Q838261", "Q37024", "Q1277557", "Q601252"]],
  ["Seychelles", "Q1042", ["Q1042"]],
  ["Sierra Leone", "Q1044", ["Q1044"]],
  ["Singapore", "Q334", ["Q334"]],
  ["Slovakia", "Q214", ["Q214"]],
  ["Slovenia", "Q215", ["Q215"]],
  ["Somalia", "Q1045", ["Q1045"]],
  ["South Africa", "Q258", ["Q258", "Q370736"]],
  ["South Korea", "Q884", ["Q884", "Q28179", "Q503585", "Q28233", "Q28208"]],
  ["Spain", "Q29", ["Q29", "Q204920", "Q217196", "Q80702", "Q199442", "Q836676", "Q3399982", "Q142417", "Q766543", "Q2721139", "Q15581", "Q8965", "Q179293", "Q303421", "Q600093", "Q1796202", "Q2039931", "Q234963", "Q2077264", "Q16254367"]],
  ["Sri Lanka", "Q854", ["Q854"]],
  ["Sudan", "Q1049", ["Q1049"]],
  ["Suriname", "Q730", ["Q730"]],
  ["Sweden", "Q34", ["Q34", "Q62589", "Q694594"]],
  ["Switzerland", "Q39", ["Q39", "Q23366230", "Q435583", "Q12724", "Q12121", "Q351537", "Q807", "Q11943", "Q2326511"]],
  ["Syria", "Q858", ["Q858", "Q146885", "Q146600", "Q131404661", "Q146562", "Q146880"]],
  ["Taiwan", "Q865", ["Q865", "Q137816", "Q2444884"]],
  ["Tajikistan", "Q863", ["Q863"]],
  ["Tanzania", "Q924", ["Q924"]],
  ["Thailand", "Q869", ["Q869", "Q1155700"]],
  ["The Bahamas", "Q778", ["Q778"]],
  ["The Gambia", "Q1005", ["Q1005"]],
  ["Timor-Leste", "Q574", ["Q574"]],
  ["Togo", "Q945", ["Q945"]],
  ["Tonga", "Q678", ["Q678"]],
  ["Trinidad and Tobago", "Q754", ["Q754"]],
  ["Tunisia", "Q948", ["Q948", "Q2017684"]],
  ["Turkey", "Q43", ["Q43", "Q12560", "Q12544", "Q335088", "Q41470", "Q47611", "Q18986", "Q208404", "Q536598", "Q1568260", "Q2022162", "Q2909425"]],
  ["Turkmenistan", "Q874", ["Q874"]],
  ["Uganda", "Q1036", ["Q1036"]],
  ["Ukraine", "Q212", ["Q212", "Q243610", "Q133356", "Q457167", "Q1508143", "Q2396442", "Q212439", "Q1108445", "Q180086", "Q3403551"]],
  ["United Arab Emirates", "Q878", ["Q878"]],
  ["United Kingdom", "Q145", ["Q145", "Q174193", "Q161885", "Q179876", "Q21", "Q22", "Q230791", "Q25", "Q248452", "Q179997", "Q785", "Q23148", "Q18348382", "Q23635", "Q25230", "Q42406", "Q251668", "Q644636", "Q795427", "Q918153"]],
  ["United States", "Q30", ["Q30", "Q156418", "Q547795", "Q617602", "Q5094611", "Q33123248", "Q16568", "Q21056", "Q27464926"]],
  ["Uruguay", "Q77", ["Q77"]],
  ["Uzbekistan", "Q265", ["Q265", "Q484195", "Q577668", "Q487829", "Q12150341"]],
  ["Vanuatu", "Q686", ["Q686"]],
  ["Venezuela", "Q717", ["Q717"]],
  ["Vietnam", "Q881", ["Q881", "Q430309", "Q6500483", "Q10841085"]],
  ["Yemen", "Q805", ["Q805"]],
  ["Zambia", "Q953", ["Q953"]],
  ["Zimbabwe", "Q954", ["Q954", "Q217169", "Q750583"]],
];

// Movements / schools (Wikidata QIDs).
const MOVEMENTS = [
  ['Q4692', 'Renaissance'], ['Q37853', 'Baroque'], ['Q131808', 'Mannerism'],
  ['Q610877', 'Northern Renaissance'], ['Q122960', 'Rococo'], ['Q14378', 'Neoclassicism'],
  ['Q37068', 'Romanticism'], ['Q10857409', 'Realism'], ['Q184814', 'Pre-Raphaelite Brotherhood'],
  ['Q40415', 'Impressionism'], ['Q166713', 'Post-Impressionism'], ['Q164800', 'Symbolism'],
  ['Q34636', 'Art Nouveau'], ['Q80113', 'Expressionism'], ['Q42934', 'Cubism'],
  ['Q131221', 'Futurism'], ['Q6034', 'Dada'], ['Q39427', 'Surrealism'],
  ['Q207103', 'Constructivism'], ['Q134147', 'Pop art'],
];
// Roles — the same five occupation roots as search (ROOTS in search.js).
const ROLES = [
  ['Q1028181', 'Painters'], ['Q1281618', 'Sculptors'], ['Q15296811', 'Draftspeople'],
  ['Q329439', 'Engravers'], ['Q11569986', 'Printmakers'],
];

const COUNTRY_BY_ID = new Map(COUNTRIES.map(([label, id, polities]) => [id, { label, polities }]));
const POLITY_TO_COUNTRIES = new Map();
for (const [, id, polities] of COUNTRIES) {
  for (const p of polities) {
    const arr = POLITY_TO_COUNTRIES.get(p) || [];
    if (!arr.includes(id)) arr.push(id);
    POLITY_TO_COUNTRIES.set(p, arr);
  }
}

const FACETS = [
  { id: 'century', label: 'By century', values: CENTURIES.map((c) => ({ id: String(c), label: centuryLabel(c) })) },
  { id: 'country', label: 'By country', values: COUNTRIES.map(([label, id]) => ({ id, label })) },
  { id: 'movement', label: 'By movement', values: MOVEMENTS.map(([id, label]) => ({ id, label })) },
  { id: 'role', label: 'By medium', values: ROLES.map(([id, label]) => ({ id, label })) },
];

function bad(msg) {
  throw Object.assign(new Error(msg), { status: 400 });
}

// Occupation subclasses per root (P279* closure), resolved once per process.
let occCache = null;
async function occValues() {
  if (occCache) return occCache;
  const rows = await sparqlWD(`SELECT ?root ?o WHERE {
    VALUES ?root { ${ROOT_VALUES} }
    ?o wdt:P279* ?root .
  }`, { timeout: 60000 });
  const map = {};
  for (const b of rows) {
    const root = qid(v(b, 'root'));
    (map[root] ||= new Set()).add(qid(v(b, 'o')));
  }
  occCache = map;
  return map;
}

// Labels for QIDs via the MediaWiki API (batched, 50 per call). A chunk
// that fails yields no labels rather than failing the whole list.
async function fetchLabels(qids) {
  const out = {};
  if (!qids.length) return out;
  const chunks = [];
  for (let i = 0; i < qids.length; i += 50) chunks.push(qids.slice(i, i + 50));
  const results = await Promise.all(
    chunks.map(async (ch) => {
      try {
        const d = await getJSON('https://www.wikidata.org/w/api.php?' + qs({ action: 'wbgetentities', ids: ch.join('|'), props: 'labels', languages: 'en', format: 'json' }), { timeout: 25000 });
        return d.entities || {};
      } catch {
        return {};
      }
    })
  );
  for (const ents of results) for (const [id, e] of Object.entries(ents)) if (e.labels?.en?.value) out[id] = e.labels.en.value;
  return out;
}

// Dynamic country list: every distinct P27 value among eligible artists,
// with artist counts, grouped under the modern country from COUNTRIES.
// Any polity not in the table appears under its own label, so the list is
// complete by construction. Cached in-process (the count query takes
// ~12s); a failed computation clears the cache so the next call retries.
let countryFacetsCache = null;
async function getCountryFacets() {
  if (countryFacetsCache) return countryFacetsCache;
  countryFacetsCache = computeCountryFacets().catch((e) => {
    countryFacetsCache = null;
    throw e;
  });
  return countryFacetsCache;
}

// Warm the country list in the background at server startup, so the first
// visitor gets the full dynamic list (351 entries with counts) instead of
// the 183-country fallback. The count query answers in ~17s from some
// networks but can exceed the 55s budget from Render, so this runs with
// the longer timeouts above and retries once after 2 minutes if it fails.
// Never blocks startup; a failed warm-up just leaves the fallback in
// place until the next request retries it.
async function warmCountryFacets() {
  try {
    const facets = await getCountryFacets();
    console.log(`Browse country list warmed: ${facets.length} countries`);
  } catch (e) {
    console.log(`Browse country warm-up failed (${e.message}); retrying in 2 minutes`);
    setTimeout(() => {
      getCountryFacets().then(
        (facets) => console.log(`Browse country list warmed on retry: ${facets.length} countries`),
        (err) => console.log(`Browse country warm-up retry failed (${err.message}); next request will retry`)
      );
    }, 120000).unref?.();
  }
}

async function computeCountryFacets() {
  const occ = await occValues();
  const occList = [...new Set(Object.values(occ).flatMap((s) => [...s]))].map((q) => 'wd:' + q);
  // COUNT(DISTINCT ?p) with the VALUES occupation form answers in ~12s
  // (2026-11-16); the same GROUP BY with the P279* join times out, and
  // adding the label service to this query pushes it past 55s — labels
  // for unmapped polities are fetched separately below.
  const rows = await sparqlWD(
    `SELECT ?c (COUNT(DISTINCT ?p) AS ?n) WHERE {
      VALUES ?o { ${occList.join(' ')} }
      ?p wdt:P27 ?c .
      ?p wdt:P106 ?o .
    } GROUP BY ?c`,
    { timeout: 120000 }
  );
  const byCountry = new Map();
  const unmapped = [];
  for (const b of rows) {
    const polity = qid(v(b, 'c'));
    const n = parseInt(v(b, 'n') || '0', 10);
    // Some artists have P27 recorded as "unknown value", which SPARQL
    // returns as a blank node (a /.well-known/genid/ URI), not a QID —
    // that is not a country, so it is skipped, not listed.
    if (!polity || !/^Q\d+$/.test(polity) || !n) continue;
    const targets = POLITY_TO_COUNTRIES.get(polity);
    if (!targets) {
      unmapped.push({ qid: polity, count: n });
      continue;
    }
    for (const t of targets) {
      const cur = byCountry.get(t) || { id: t, label: COUNTRY_BY_ID.get(t).label, count: 0, historical: false };
      cur.count += n;
      byCountry.set(t, cur);
    }
  }
  // Counts are summed per polity: an artist with two citizenships counts
  // under both, so a country's count is a scale indicator, not a distinct
  // headcount.
  const labels = await fetchLabels(unmapped.map((u) => u.qid));
  for (const u of unmapped) {
    // A place can be both a group target and a polity in its own right
    // (Hong Kong: British Hong Kong maps to it, and artists also carry
    // P27 = Hong Kong directly; same for Palestine). Those artists belong
    // to the group — merge them in instead of overwriting it.
    const existing = byCountry.get(u.qid);
    if (existing) {
      existing.count += u.count;
      continue;
    }
    byCountry.set(u.qid, { id: u.qid, label: labels[u.qid] || u.qid, count: u.count, historical: true });
  }
  return [...byCountry.values()]
    .map((c) => ({ id: c.id, label: c.label, count: c.count, historical: !!c.historical }))
    .sort((a, b) => a.historical - b.historical || a.label.localeCompare(b.label));
}

// Facet definitions for the no-params response. The country values are
// dynamic; if the live count fails, the static table is returned instead.
async function getFacets() {
  let countries = null;
  let countryError = null;
  try {
    countries = await getCountryFacets();
  } catch (e) {
    countryError = e.message || String(e);
  }
  const facets = [
    { id: 'century', label: 'By century', values: CENTURIES.map((c) => ({ id: String(c), label: centuryLabel(c) })) },
    { id: 'country', label: 'By country', values: countries || COUNTRIES.map(([label, id]) => ({ id, label })) },
    { id: 'movement', label: 'By movement', values: MOVEMENTS.map(([id, label]) => ({ id, label })) },
    { id: 'role', label: 'By medium', values: ROLES.map(([id, label]) => ({ id, label })) },
  ];
  return { facets, countryError };
}

// Label for a country id: the static table, else a live label lookup,
// else the QID itself (an unmapped polity id).
async function countryLabel(id) {
  if (COUNTRY_BY_ID.has(id)) return COUNTRY_BY_ID.get(id).label;
  const labels = await fetchLabels([id]);
  return labels[id] || id;
}

function facetFilter(facet, value) {
  if (facet === 'century') {
    const c = parseInt(value, 10);
    const from = `${(c - 1) * 100 + 1}-01-01T00:00:00Z`;
    const to = `${c * 100 + 1}-01-01T00:00:00Z`;
    return `?p wdt:P569 ?bt . FILTER(?bt >= "${from}"^^xsd:dateTime && ?bt < "${to}"^^xsd:dateTime)`;
  }
  if (facet === 'movement') return `?p wdt:P135 wd:${value} .`;
  // role: the occupation VALUES list is already restricted to this root's
  // subclasses, so no extra pattern is needed. country: see rankCountry —
  // it uses its own query shape (P279* join, polity list).
  return '';
}

// Ranking query shapes, tuned per facet against Wikidata (2026-11-16):
// - ORDER BY sitelinks in SPARQL is fast when the joined set is small
//   (century, movement, role) but times out for country, where the set is
//   huge — country uses per-polity thresholded windows and sorts in JS
//   (see rankCountry).
// - threshold: only artists with at least that many sitelinks are ranked.
//   A second pass at a lower threshold fills up thin facets.
// - limit: rows returned; several rows per artist (one per occupation), so
//   200 rows yield ~50–80 distinct artists.
const RANK = {
  century: [{ threshold: null, limit: 200, order: true }],
  movement: [{ threshold: null, limit: 200, order: true }],
  role: [
    { threshold: 40, limit: 200, order: true },
    { threshold: 10, limit: 200, order: true },
  ],
};

async function rankRanked(facet, value, occList) {
  for (const cfg of RANK[facet]) {
    const thresh = cfg.threshold != null ? `FILTER(?links >= ${cfg.threshold})` : '';
    const order = cfg.order ? 'ORDER BY DESC(?links)' : '';
    const q = `SELECT ?p ?links WHERE {
      VALUES ?o { ${occList.join(' ')} }
      ${facetFilter(facet, value)}
      ?p wdt:P106 ?o .
      ?p wikibase:sitelinks ?links . ${thresh}
    } ${order} LIMIT ${cfg.limit}`;
    const r = await safe('Wikidata', () => sparqlWD(q, { timeout: 55000 }));
    if (!r.ok) return { ok: false, error: r.error };
    const linksByQ = new Map();
    for (const b of r.data || []) {
      const id = qid(v(b, 'p'));
      if (!linksByQ.has(id)) linksByQ.set(id, parseInt(v(b, 'links') || '0', 10));
    }
    const ranked = [...linksByQ.entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);
    if (ranked.length >= 50 || cfg === RANK[facet][RANK[facet].length - 1]) return { ok: true, ranked, linksByQ, errors: [] };
  }
  return { ok: true, ranked: [], linksByQ: new Map(), errors: [] };
}

// Country ranking: citizenship (P27) over the country's historical
// polities, with the P279* occupation join, one query PER polity run in
// parallel and merged in JS. A single query over the whole polity list
// returns an arbitrary 500-row window that can crowd out a whole polity
// (the Holy Roman Empire's set hid Dürer, Raphael and Hildegard from
// Germany, 2026-11-16); per-polity windows are small and complete (HRE:
// 29 artists, Bavaria: 1). The VALUES occupation form that works for
// century/movement/role times out for the big polities (Kingdom of the
// Netherlands failed at every threshold); the P279* form answers in
// ~1–30s per polity and finds the masters. A polity query that fails is
// recorded in `errors` and the rest still merge, so one slow polity cannot
// sink the list.
//
// A ladder of sitelink thresholds fills thin lists: Mexico has 1,270
// eligible artists but only 17 with 20+ sitelinks, so a single >=20 pass
// returned 17 (2026-11-16). Each pass adds the next tier (>=10, then >=5)
// until 50 artists are found; the 500-row window is arbitrary, so a single
// low-threshold pass over a big polity could crowd out its top artists —
// the ladder keeps the top correct and only fills from below.
const COUNTRY_THRESHOLDS = [20, 10, 5];
async function rankCountry(polities, extra = '') {
  const linksByQ = new Map();
  const errorSet = new Set();
  for (const thresh of COUNTRY_THRESHOLDS) {
    if (linksByQ.size >= 50) break;
    const settled = await Promise.allSettled(
      polities.map((p) =>
        safe('Wikidata', () =>
          sparqlWD(
            `SELECT ?p ?links WHERE {
              VALUES ?root { ${ROOT_VALUES} }
              ?p wdt:P27 wd:${p} .
              ?p wdt:P106 ?o . ?o wdt:P279* ?root .
              ${extra}
              ?p wikibase:sitelinks ?links . FILTER(?links >= ${thresh})
            } LIMIT 500`,
            { timeout: 55000 }
          )
        )
      )
    );
    for (const s of settled) {
      if (s.status === 'fulfilled' && s.value.ok) {
        for (const b of s.value.data || []) {
          const id = qid(v(b, 'p'));
          if (!linksByQ.has(id)) linksByQ.set(id, parseInt(v(b, 'links') || '0', 10));
        }
      } else {
        errorSet.add(s.status === 'fulfilled' ? s.value.error : String(s.reason));
      }
    }
  }
  const ranked = [...linksByQ.entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);
  return { ok: true, ranked, linksByQ, errors: [...errorSet] };
}

// Combined ranking without a country: century + movement + role, ANDed,
// ranked by sitelinks. No threshold — combined sets are small, and ORDER BY
// returns the best-documented first.
async function rankCombinedNoCountry(filters, occList) {
  const parts = [];
  if (filters.century) parts.push(facetFilter('century', filters.century));
  if (filters.movement) parts.push(`?p wdt:P135 wd:${filters.movement} .`);
  const q = `SELECT ?p ?links WHERE {
    VALUES ?o { ${occList.join(' ')} }
    ${parts.join('\n')}
    ?p wdt:P106 ?o .
    ?p wikibase:sitelinks ?links .
  } ORDER BY DESC(?links) LIMIT 300`;
  const r = await safe('Wikidata', () => sparqlWD(q, { timeout: 55000 }));
  if (!r.ok) return { ok: false, error: r.error };
  const linksByQ = new Map();
  for (const b of r.data || []) {
    const id = qid(v(b, 'p'));
    if (!linksByQ.has(id)) linksByQ.set(id, parseInt(v(b, 'links') || '0', 10));
  }
  const ranked = [...linksByQ.entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);
  return { ok: true, ranked, linksByQ, errors: [] };
}

// Details for the top 50 ranked artists (same VALUES + OPTIONAL pattern
// as search), assembled into browse cards.
async function fetchDetails(topIds, allowedOcc, linksByQ) {
  const r2 = await safe('Wikidata', () =>
    sparqlWD(`SELECT ?p ?pLabel ?b ?d ?bplLabel ?ulan ?img ?links ?o ?oLabel WHERE {
      VALUES ?p { ${topIds.map((id) => 'wd:' + id).join(' ')} }
      OPTIONAL { ?p p:P569/psv:P569 [ wikibase:timeValue ?b ] }
      OPTIONAL { ?p p:P570/psv:P570 [ wikibase:timeValue ?d ] }
      OPTIONAL { ?p wdt:P19 ?bpl }
      OPTIONAL { ?p wdt:P245 ?ulan }
      OPTIONAL { ?p wdt:P18 ?img }
      OPTIONAL { ?p wikibase:sitelinks ?links }
      OPTIONAL { ?p wdt:P106 ?o }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "${LANGS}". }
    }`)
  );
  if (!r2.ok) return { ok: false, error: r2.error };
  const byQ = {};
  for (const b of r2.data || []) {
    const id = qid(v(b, 'p'));
    let a = byQ[id];
    if (!a) {
      const bp = v(b, 'bplLabel');
      a = byQ[id] = {
        id,
        name: v(b, 'pLabel'),
        birthYear: wdYear(v(b, 'b')),
        deathYear: wdYear(v(b, 'd')),
        birthPlace: bp && !/^https?:/.test(bp) ? bp : null,
        roles: new Set(),
        image: v(b, 'img') ? v(b, 'img').replace(/^http:/, 'https:') + '?width=160' : null,
        ulan: v(b, 'ulan') || null,
        sitelinks: linksByQ.get(id) || parseInt(v(b, 'links') || '0', 10),
      };
    }
    // Show only the occupations that make the artist eligible here.
    if (v(b, 'o') && allowedOcc.has(qid(v(b, 'o'))) && v(b, 'oLabel')) a.roles.add(v(b, 'oLabel'));
    if (!a.ulan && v(b, 'ulan')) a.ulan = v(b, 'ulan');
  }
  const artists = topIds
    .map((id) => byQ[id])
    .filter(Boolean)
    .map((a) => ({ ...a, roles: [...a.roles].filter((x) => x && !/old master/i.test(x)) }));
  // Best-documented first; ties broken by birth year (earliest first),
  // as the browse page states.
  artists.sort((a, b) => b.sitelinks - a.sitelinks || (a.birthYear ?? 9999) - (b.birthYear ?? 9999));
  return { ok: true, artists };
}

/**
 * browse({facet, value}) — one facet at a time (legacy URLs keep working).
 * browse({century, country, movement, role}) — any combination, ANDed.
 * browse({}) — {facets: [...]}. If both a single facet and combined params
 * are given, the combined params win.
 */
async function browse(params) {
  const { facet, value, century, country, movement, role } = params || {};
  const hasCombined = Boolean(century || country || movement || role);
  if (!facet && !value && !hasCombined) {
    const { facets, countryError } = await getFacets();
    return { facets, errors: countryError ? [countryError] : [] };
  }
  if (hasCombined) return browseCombined({ century, country, movement, role });

  if (!facet || !value) bad('Browse needs both a facet and a value.');
  const f = FACETS.find((x) => x.id === facet);
  if (!f) bad(`Unknown facet: ${facet}`);
  let label;
  if (facet === 'country') {
    // A modern country id from the table, or any polity QID (an unmapped
    // polity appears under its own label).
    if (!/^Q\d+$/.test(value)) bad(`Unknown value for ${facet}: ${value}`);
    label = await countryLabel(value);
  } else {
    const val = f.values.find((x) => x.id === value);
    if (!val) bad(`Unknown value for ${facet}: ${value}`);
    label = val.label;
  }

  const occ = await safe('Wikidata', occValues);
  if (!occ.ok) return { facet, value, label, artists: [], errors: [occ.error] };
  const occList =
    facet === 'role'
      ? [...(occ.data[value] || [])].map((q) => 'wd:' + q)
      : [...new Set(Object.values(occ.data).flatMap((s) => [...s]))].map((q) => 'wd:' + q);
  const allowedOcc = new Set(occList.map((s) => s.slice(3)));

  const r1 =
    facet === 'country'
      ? await rankCountry(COUNTRY_BY_ID.get(value)?.polities || [value])
      : await rankRanked(facet, value, occList);
  if (!r1.ok) return { facet, value, label, artists: [], errors: [r1.error] };
  const { ranked, linksByQ } = r1;
  const rankErrors = r1.errors || [];
  const topIds = ranked.slice(0, 50);
  if (!topIds.length) return { facet, value, label, artists: [], errors: rankErrors };

  const r2 = await fetchDetails(topIds, allowedOcc, linksByQ);
  if (!r2.ok) return { facet, value, label, artists: [], errors: [r2.error] };
  return { facet, value, label, artists: r2.artists, errors: rankErrors };
}

async function browseCombined(filters) {
  if (filters.century && !CENTURIES.includes(parseInt(filters.century, 10))) bad(`Unknown century: ${filters.century}`);
  if (filters.country && !/^Q\d+$/.test(filters.country)) bad(`Unknown country: ${filters.country}`);
  if (filters.movement && !MOVEMENTS.some(([id]) => id === filters.movement)) bad(`Unknown movement: ${filters.movement}`);
  if (filters.role && !ROLES.some(([id]) => id === filters.role)) bad(`Unknown role: ${filters.role}`);

  const labelParts = [];
  if (filters.century) labelParts.push(centuryLabel(parseInt(filters.century, 10)));
  if (filters.country) labelParts.push(await countryLabel(filters.country));
  if (filters.movement) labelParts.push(MOVEMENTS.find(([id]) => id === filters.movement)[1]);
  if (filters.role) labelParts.push(ROLES.find(([id]) => id === filters.role)[1]);
  const label = labelParts.join(' · ');

  const occ = await safe('Wikidata', occValues);
  if (!occ.ok) return { filters, label, artists: [], errors: [occ.error] };
  const occList =
    filters.role
      ? [...(occ.data[filters.role] || [])].map((q) => 'wd:' + q)
      : [...new Set(Object.values(occ.data).flatMap((s) => [...s]))].map((q) => 'wd:' + q);
  const allowedOcc = new Set(occList.map((s) => s.slice(3)));

  let r1;
  if (filters.country) {
    // Country plus the other filters, ANDed, on the per-polity ladder.
    // The role restriction is an extra P279* path on the same ?o.
    const extra = [
      filters.century ? facetFilter('century', filters.century) : '',
      filters.movement ? `?p wdt:P135 wd:${filters.movement} .` : '',
      filters.role ? `?o wdt:P279* wd:${filters.role} .` : '',
    ]
      .filter(Boolean)
      .join('\n');
    r1 = await rankCountry(COUNTRY_BY_ID.get(filters.country)?.polities || [filters.country], extra);
  } else {
    r1 = await rankCombinedNoCountry(filters, occList);
  }
  if (!r1.ok) return { filters, label, artists: [], errors: [r1.error] };
  const { ranked, linksByQ } = r1;
  const rankErrors = r1.errors || [];
  const topIds = ranked.slice(0, 50);
  if (!topIds.length) return { filters, label, artists: [], errors: rankErrors };

  const r2 = await fetchDetails(topIds, allowedOcc, linksByQ);
  if (!r2.ok) return { filters, label, artists: [], errors: [r2.error] };
  return { filters, label, artists: r2.artists, errors: rankErrors };
}

module.exports = { browse, FACETS, warmCountryFacets };
