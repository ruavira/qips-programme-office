import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const out = "/private/tmp/qips-wave2-model/output";
await fs.mkdir(out, { recursive: true });
const wb = Workbook.create();
const summary = wb.worksheets.add("Summary");
const assumptions = wb.worksheets.add("Assumptions");
const model = wb.worksheets.add("Model");
const scenarios = wb.worksheets.add("Scenarios");
const checks = wb.worksheets.add("Checks");
const sources = wb.worksheets.add("Sources");

const colors = { navy: "#16324F", teal: "#0F5257", aqua: "#DFF3F5", sky: "#DCEEFF", cream: "#FFF9F1", coral: "#F28C68", white: "#FFFFFF", yellow: "#FFF2CC", green: "#E2F0D9", red: "#FCE4D6", grey: "#5B6573", blue: "#0070C0" };
const title = (s, range, text) => {
  s.getRange(range).merge(); s.getRange(range.split(":")[0]).values = [[text]];
  s.getRange(range).format = { fill: colors.navy, font: { bold: true, color: colors.white, size: 16 }, rowHeight: 30, verticalAlignment: "center" };
};
const header = (s, range) => { s.getRange(range).format = { fill: colors.teal, font: { bold: true, color: colors.white }, wrapText: true, verticalAlignment: "center" }; };
const inputBlue = (s, range) => { s.getRange(range).format.font = { color: colors.blue }; };
const linkedGreen = (s, range) => { s.getRange(range).format.font = { color: "#008000" }; };
const setup = (s, widths) => { s.showGridLines = false; s.freezePanes.freezeRows(3); widths.forEach(([c,w]) => s.getRange(`${c}:${c}`).format.columnWidth = w); };

setup(summary, [["A",28],["B",24],["C",38],["D",18]]);
title(summary, "A1:D1", "QIPS pricing & unit economics — decision control");
summary.getRange("A2:D2").merge(); summary.getRange("A2").values = [["Version 2.0 · 29 July 2026 · Working model — no price or launch authorised"]];
summary.getRange("A2:D2").format = { fill: colors.aqua, font: { italic: true, color: colors.navy }, wrapText: true };
summary.getRange("A4:C4").values = [["Control", "Current output", "Meaning"]]; header(summary,"A4:C4");
summary.getRange("A5:A11").values = [["Model status"],["Missing required inputs"],["Proposed cohort seats"],["Gross revenue (reference proposal)"],["Net revenue after processor"],["Total delivery cost"],["Operating result"]];
summary.getRange("B5:B11").formulas = [["=IF(Checks!B5=0,\"READY FOR DECISION REVIEW\",\"DECISION INCOMPLETE\")"],["=Checks!B5"],["=Model!B12"],["=Model!B13"],["=Model!B15"],["=Model!B22"],["=Model!B23"]];
linkedGreen(summary,"B5:B11");
summary.getRange("C5:C11").values = [["Must read DECISION INCOMPLETE while any required input is missing."],["Count of assumptions marked MISSING."],["F025 proposal only; not capacity approval."],["Uses F024 proposed prices and illustrative mix."],["Processor scenario only; taxes and FX still unresolved."],["Incomplete while cost inputs are missing."],["Not a decision output until the gate passes."]];
summary.getRange("A13:D13").merge(); summary.getRange("A13").values = [["Required next evidence"]]; summary.getRange("A13:D13").format = { fill: colors.coral, font: { bold: true, color: colors.navy } };
summary.getRange("A14:D18").values = [
  ["Insurance and legal","Indemnity premium, exclusions and per-person treatment","Owner: W17 / Q001","MISSING"],
  ["Delivery","Faculty/coaching, platform, host/preceptor and credential costs","Owners: W02/W03/W04/W05","MISSING"],
  ["Commercial","Partner shares, tax, FX, refunds, scholarships and payment route","Owner: W16 / Q004","MISSING"],
  ["Demand","Verified denominator, tier mix, yield and capacity","Owner: W14 / Q006","MISSING"],
  ["Reimbursement","Primary ITF terms; booked at zero until verified","Owner: W16 / Q007","MISSING"]
];
summary.getRange("A14:D18").format = { fill: colors.yellow, wrapText: true };
summary.getRange("B8:B11").format.numberFormat = "$#,##0";

setup(assumptions, [["A",22],["B",34],["C",16],["D",18],["E",18],["F",54]]);
title(assumptions,"A1:F1","Assumptions and evidence status");
assumptions.getRange("A2:F2").merge(); assumptions.getRange("A2").values = [["Blue = editable input · PROPOSED is not approved · MISSING keeps the publication gate closed"]]; assumptions.getRange("A2:F2").format = { fill: colors.aqua, font:{italic:true,color:colors.navy} };
assumptions.getRange("A4:F4").values = [["Category","Input","Value","Unit","Status","Evidence / note"]]; header(assumptions,"A4:F4");
const ar = [
  ["Demand","Cohort seats",50,"people","PROPOSED","F025; floor/cap are also proposed"],
  ["Demand","International seats",5,"people","PROPOSED","Illustrative mix only"],
  ["Demand","UMIC seats",5,"people","PROPOSED","Illustrative mix only"],
  ["Demand","LMIC institutional seats",15,"people","PROPOSED","Illustrative mix only"],
  ["Demand","LMIC individual seats",20,"people","PROPOSED","Illustrative mix only"],
  ["Demand","LIC seats",5,"people","PROPOSED","Illustrative mix only"],
  ["Price","International price",3000,"USD/person","PROPOSED","F024"],
  ["Price","UMIC price",1200,"USD/person","PROPOSED","F024"],
  ["Price","LMIC institutional price",900,"USD/person","PROPOSED","F024"],
  ["Price","LMIC individual price",600,"USD/person","PROPOSED","F024"],
  ["Price","LIC price",400,"USD/person","PROPOSED","F024"],
  ["Payment","Blended processor fee",0.039,"% gross revenue","PROPOSED","Conservative Paystack international scenario; route unresolved"],
  ["Cost","Fixed programme delivery",0,"USD","MISSING","Faculty, platform, management and content"],
  ["Cost","Indemnity",0,"USD","MISSING","Q001 / W17"],
  ["Cost","Credential and recognition",0,"USD","MISSING","Q002 / W03"],
  ["Cost","Host and preceptor",0,"USD/person","MISSING","W04"],
  ["Cost","Variable delivery",0,"USD/person","MISSING","Materials, support, certificates"],
  ["Cost","Coaching group step cost",0,"USD/group","MISSING","W05"],
  ["Cost","Coaching group capacity",8,"people/group","PROPOSED","Must be calibrated"],
  ["Commercial","Partner/revenue share",0,"% net revenue","MISSING","Q004"],
  ["Commercial","Tax and FX leakage",0,"% gross revenue","MISSING","Country-specific treatment required"],
  ["Commercial","Refund and bad debt",0,"% gross revenue","MISSING","Policy and evidence required"],
  ["Commercial","Scholarship subsidy",0,"USD","MISSING","Authority, pool and eligibility required"]
];
assumptions.getRange(`A5:F${4+ar.length}`).values = ar;
inputBlue(assumptions,`C5:C${4+ar.length}`);
assumptions.getRange("C11:C15").format.numberFormat = "$#,##0";
assumptions.getRange("C16").format.numberFormat = "0.0%";
assumptions.getRange("C17:C22").format.numberFormat = "$#,##0";
assumptions.getRange("C24:C26").format.numberFormat = "0.0%";
assumptions.getRange("A5:F27").format.wrapText = true;
assumptions.getRange("A17:F18").format.fill = colors.yellow;
assumptions.getRange("A19:F22").format.fill = colors.yellow;
assumptions.getRange("A24:F27").format.fill = colors.yellow;

setup(model, [["A",32],["B",20],["C",26],["D",22]]);
title(model,"A1:D1","Reference proposal model");
model.getRange("A2:D2").merge(); model.getRange("A2").values = [["Formula-driven view; financial conclusions are invalid while Checks!B5 is greater than zero"]]; model.getRange("A2:D2").format = { fill: colors.aqua, font:{italic:true,color:colors.navy} };
model.getRange("A4:D4").values = [["Tier","Seats","Price","Gross revenue"]]; header(model,"A4:D4");
model.getRange("A5:A9").values = [["International"],["UMIC"],["LMIC institutional"],["LMIC individual"],["LIC"]];
model.getRange("B5:D9").formulas = [
  ["=Assumptions!C6","=Assumptions!C11","=B5*C5"],
  ["=Assumptions!C7","=Assumptions!C12","=B6*C6"],
  ["=Assumptions!C8","=Assumptions!C13","=B7*C7"],
  ["=Assumptions!C9","=Assumptions!C14","=B8*C8"],
  ["=Assumptions!C10","=Assumptions!C15","=B9*C9"]
]; linkedGreen(model,"B5:D9");
model.getRange("A12:A23").values = [["Total seats"],["Gross revenue"],["Processor fee"],["Net revenue after processor"],["Fixed programme delivery"],["Indemnity"],["Credential and recognition"],["Host + variable delivery"],["Coaching groups"],["Coaching step cost"],["Total delivery cost"],["Operating result"]];
model.getRange("B12:B23").formulas = [
  ["=SUM(B5:B9)"],["=SUM(D5:D9)"],["=B13*Assumptions!C16"],["=B13-B14"],["=Assumptions!C17"],["=Assumptions!C18"],["=Assumptions!C19"],["=B12*(Assumptions!C20+Assumptions!C21)"],["=ROUNDUP(B12/Assumptions!C23,0)"],["=B20*Assumptions!C22"],["=SUM(B16:B19)+B21+Assumptions!C27+B15*Assumptions!C24+B13*(Assumptions!C25+Assumptions!C26)"],["=IF(Checks!B5=0,B15-B22,0)"]
  ]; linkedGreen(model,"B12:B23");
model.getRange("B13:B23").format.numberFormat = "$#,##0"; model.getRange("B12").format.numberFormat = "0";
model.getRange("B5:B9").format.numberFormat = "0"; model.getRange("C5:D9").format.numberFormat = "$#,##0"; model.getRange("B20").format.numberFormat = "0";
model.getRange("C23:D23").merge(); model.getRange("C23").values = [["Zero shown while decision gate is incomplete; not a projected result."]]; model.getRange("C23:D23").format = { fill: colors.yellow, wrapText:true };

setup(scenarios, [["A",25],["B",18],["C",18],["D",18],["E",34]]);
title(scenarios,"A1:E1","Scenario frame");
scenarios.getRange("A3:E3").values = [["Scenario","Seats","Price factor","Cost factor","Use"]]; header(scenarios,"A3:E3");
scenarios.getRange("A4:E6").values = [
  ["Reference proposal",50,1,1,"F024/F025 proposal; not approved"],
  ["Lower demand",40,1,1.15,"Stress frame; costs still missing"],
  ["Cost stress",50,1,1.30,"Stress frame; costs still missing"]
]; inputBlue(scenarios,"B4:D6"); scenarios.getRange("C4:D6").format.numberFormat = "0%";
scenarios.getRange("A8:E8").merge(); scenarios.getRange("A8").values = [["No scenario is decision-ready until required assumptions are verified. Values above are controls, not forecasts."]]; scenarios.getRange("A8:E8").format = { fill: colors.yellow, wrapText:true };

setup(checks, [["A",38],["B",26],["C",48]]);
title(checks,"A1:C1","Model checks and publication gate");
checks.getRange("A3:C3").values = [["Check","Result","Pass condition"]]; header(checks,"A3:C3");
checks.getRange("A4:A10").values = [["Required input rows"],["Missing required inputs"],["Seat mix equals cohort"],["Prices are approved"],["Demand evidence is verified"],["Commercial terms are approved"],["Publication gate"]];
checks.getRange("B4:B10").formulas = [["=COUNTIF(Assumptions!E5:E27,\"MISSING\")+COUNTIF(Assumptions!E5:E27,\"VERIFIED\")"],["=COUNTIF(Assumptions!E5:E27,\"MISSING\")"],["=IF(SUM(Assumptions!C6:C10)=Assumptions!C5,\"PASS\",\"FAIL\")"],["=IF(COUNTIF(Assumptions!E11:E15,\"APPROVED\")=5,\"PASS\",\"FAIL\")"],["=IF(Assumptions!E5=\"VERIFIED\",\"PASS\",\"FAIL\")"],["=IF(COUNTIF(Assumptions!E24:E27,\"VERIFIED\")=4,\"PASS\",\"FAIL\")"],["=IF(AND(B5=0,B6=\"PASS\",B7=\"PASS\",B8=\"PASS\",B9=\"PASS\"),\"PASS\",\"FAIL\")"]]; linkedGreen(checks,"B4:B10");
checks.getRange("C4:C10").values = [["Inventory only"],["Must be zero"],["PASS"],["Five APPROVED price rows"],["Verified cohort/mix"],["Four verified commercial rows"],["All preceding controls pass"]];
checks.getRange("A12:C12").merge(); checks.getRange("A12").values = [["Expected current result: FAIL. Changing this to PASS requires evidence and approval, not formatting."]]; checks.getRange("A12:C12").format = { fill: colors.coral, font:{bold:true,color:colors.navy}, wrapText:true };

setup(sources, [["A",24],["B",38],["C",92],["D",18]]);
title(sources,"A1:D1","Sources and access record");
sources.getRange("A3:D3").values = [["Source","Use","URL / reference","Accessed"]]; header(sources,"A3:D3");
sources.getRange("A4:D12").values = [
  ["QIPS canon F024–F027","Proposed prices/capacity/trigger","canon/facts.yaml","2026-07-29"],
  ["ISQua Fellowship","Income-band and group pricing","https://isqua.org/fellowship/","2026-07-29"],
  ["IHI Improvement Advisor","Premium applied comparator","https://www.ihi.org/learn/courses/improvement-advisor-professional-development-program-united-states","2026-07-29"],
  ["NAHQ CPHQ apply","Credential price comparator","https://nahq.org/credentials/cphq-certified-professional-in-healthcare-quality/apply/","2026-07-29"],
  ["AUC operational excellence diploma","Regional price/payment comparator","https://business.aucegypt.edu/execed/individual-programs/healthcare/hospital-management-operational-excellence-diploma","2026-07-29"],
  ["Paystack pricing","Processor fees","https://dr.paystack.com/pricing","2026-07-29"],
  ["Paystack Terminal","Nigeria/Ghana methods","https://dr.paystack.com/terminal/","2026-07-29"],
  ["Stripe global","Country availability","https://stripe.com/global","2026-07-29"],
  ["World Bank FY27","Income group maintenance","https://blogs.worldbank.org/en/opendata/who-moves-up-and-why--a-closer-look-at-the-new-world-bank-group-","2026-07-29"]
]; sources.getRange("A4:D12").format.wrapText = true;

for (const s of [summary,assumptions,model,scenarios,checks,sources]) {
  const used = s.getUsedRange(); used.format.verticalAlignment = "top";
}
const names = ["Summary","Assumptions","Model","Scenarios","Checks","Sources"];
for (const name of names) {
  const preview = await wb.render({ sheetName:name, autoCrop:"all", scale:1, format:"png" });
  await fs.writeFile(`${out}/${name.toLowerCase()}.png`, new Uint8Array(await preview.arrayBuffer()));
}
const inspection = await wb.inspect({ kind:"formula", sheetId:"Model", range:"A1:D25", maxChars:12000, options:{maxResults:100} });
await fs.writeFile(`${out}/formula-inspection.txt`, inspection.ndjson || String(inspection));
const errorScan = await wb.inspect({ kind:"match", searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options:{useRegex:true,maxResults:100}, maxChars:12000 });
await fs.writeFile(`${out}/error-scan.txt`, errorScan.ndjson || String(errorScan));
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(`${out}/QIPS-Pricing-and-Unit-Economics-Model-v2.xlsx`);
console.log(JSON.stringify({output:`${out}/QIPS-Pricing-and-Unit-Economics-Model-v2.xlsx`, previews:names.map(n=>`${out}/${n.toLowerCase()}.png`)}));
