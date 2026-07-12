/**
 * Embeds operator portraits and skill icons directly into cells of the
 * Mastery Priority Google Sheet, using Sheets' native in-cell image type
 * (SpreadsheetApp.newCellImage) rather than an =IMAGE() formula. Google
 * fetches each image once at insert time and keeps its own copy, so nothing
 * needs to stay hosted afterward.
 *
 * Images are sourced from the public ArknightsGuideAssets repo (the same
 * submodule the site itself uses), via raw.githubusercontent.com — no
 * hosting setup required. Operator identity is resolved by matching the
 * sheet's operator-name cell against the "appellation" field in
 * character_table.json, the same source of truth used by
 * tools/build_article_variants.py.
 *
 * SHEET LAYOUT this script expects (a "website-like" block per operator,
 * not a plain table — see CONFIG to tune the offsets):
 *   - Operator name: a merged cell starting at column A of the operator's
 *     "start row" (e.g. A6:H6 for the first operator, if START_ROW = 6).
 *   - Portrait: a merged cell starting PORTRAIT_ROW_OFFSET rows below the
 *     name row, at column PORTRAIT_COL_START (e.g. A7:C10 for Wang).
 *   - Rarity stars + colors: a merged cell in the same row as the top of
 *     the portrait, at STAR_COL_START (e.g. D7:F7 for Wang, to the right
 *     of the A7:C10 portrait), filled with the operator's rarity as ★
 *     characters (from the "rarity" field in character_table.json, e.g.
 *     "TIER_6" -> "★★★★★★"). The font color of both this cell and the
 *     name row is set based on rarity via RARITY_COLORS.
 *   - Subclass name: a merged cell directly below the stars, same column
 *     (e.g. D8:F8 for Wang), filled with the English subclass name looked
 *     up from uniequip_table.json's subProfDict, keyed by the operator's
 *     subProfessionId from character_table.json (e.g. "traper" ->
 *     "Trapmaster"). Falls back to "TBD" if that subclass has no English
 *     translation yet.
 *   - Subclass icon: a merged cell spanning 2 rows x 2 columns to the right
 *     of the stars/subclass name, at (star row, SUBCLASS_ICON_COL_START)
 *     (e.g. G7:H8 for Wang), from assets/game_img/subprofessionicon
 *     (e.g. sub_traper_icon.png).
 *   - Skill icons: one row per skill, starting SKILL_ROW_OFFSET rows below
 *     the name row and going down one row per skill (e.g. Wang's S3 row is
 *     row 12, S2 is row 13, S1 is row 14). Each row already has a skill
 *     label like "S3M3" in SKILL_LABEL_COL (used both to read the skill
 *     number and to detect how many skill rows this operator has — the
 *     scan stops at the first row with a blank/non-matching label), and
 *     the icon is written to SKILL_ICON_COL of that same row.
 *   - The next operator's block starts on the first non-blank row after a
 *     row that's blank across all NAME_COL_SPAN columns (e.g. A:H) — this
 *     scan begins right after the last detected skill row, so the
 *     intentional blank spacer row between the portrait and the first
 *     skill row is never mistaken for the block separator.
 *   - A section-divider sequence (blank row, a row whose text matches one
 *     of SECTION_DIVIDER_TEXTS, another blank row) can appear between
 *     operator blocks — e.g. blank(A:J) + "Other Updates" (A:J) +
 *     blank(A:J) before more operators resume. The script detects and
 *     skips over these instead of treating the divider text as an
 *     operator name.
 *
 * SETUP
 *   1. Open the spreadsheet -> Extensions -> Apps Script.
 *   2. Paste this whole file in as a script file (e.g. Code.gs).
 *   3. Edit the CONFIG block below to match your sheet's tab name and
 *      row/column offsets.
 *   4. Select the embedOperatorImages function in the toolbar and click Run.
 *      The first run will prompt for authorization (UrlFetch + Sheets).
 *   5. Check the execution log (View -> Logs) and/or the alert dialog for a
 *      summary of anything that couldn't be embedded.
 *
 * This script is idempotent — re-running it just overwrites the same cells,
 * so it's safe to run again after adding new operator blocks.
 */

const CONFIG = {
  // Tab name containing the operator blocks.
  SHEET_NAME: "Masteries", // <-- EDIT to match your sheet's tab name

  // Row of the FIRST operator's merged name cell (e.g. 6 for A6:H6).
  START_ROW: 6, // <-- EDIT

  // Number of columns the name row spans, starting at column A (A:H = 8).
  // Used both to read the name and to detect the blank separator row.
  NAME_COL_SPAN: 8, // <-- EDIT

  EMBED_PORTRAITS: true,
  // Portrait's merged range starts this many rows below the name row
  // (e.g. name row 6 -> portrait starts row 7) and at this column
  // (1 = column A).
  PORTRAIT_ROW_OFFSET: 1, // <-- EDIT
  PORTRAIT_COL_START: 1, // <-- EDIT

  SET_RARITY_STYLING: true,
  // Column of the rarity-stars cell, same row as the top of the portrait
  // (e.g. 4 = column D, immediately right of an A:C portrait).
  STAR_COL_START: 4, // <-- EDIT
  // Font color applied to both the rarity-stars cell and the name row,
  // keyed by the numeric rarity extracted from character_table.json's
  // "rarity" field (e.g. "TIER_6" -> 6). Add entries for other rarities
  // if/when they show up.
  RARITY_COLORS: {
    6: "#ff6d01",
    5: "#fbbc04",
    4: "#d4a6bd",
  },

  SET_SUBCLASS_INFO: true,
  // Subclass name goes directly below the stars, in STAR_COL_START. Subclass
  // icon column is to the right of the stars/name (e.g. 7 = column G, for a
  // G:H icon merge spanning the star row and the row below it).
  SUBCLASS_ICON_COL_START: 7, // <-- EDIT

  // First skill row = name row + this offset (e.g. name row 6 -> row 12).
  // Subsequent skills go one row further down each time.
  SKILL_ROW_OFFSET: 6, // <-- EDIT

  // Column holding each skill row's existing "S#M#" label (1 = column A),
  // used to read the skill number and to detect how many skill rows this
  // operator has (stops at the first blank/non-matching label).
  SKILL_LABEL_COL: 1, // <-- EDIT

  // Column the skill icon gets written to, in the same row as the label
  // (2 = column B).
  SKILL_ICON_COL: 2, // <-- EDIT

  // Text (case-insensitive, exact match after trimming) of any standalone
  // section-divider rows that can appear between operator blocks — each
  // looks like blank(A:J) + this text merged across A:J + another
  // blank(A:J). Add more strings here if other section headers show up.
  SECTION_DIVIDER_TEXTS: ["Other Updates"], // <-- EDIT if needed

  // If true, checks each image URL resolves before embedding and reports
  // any that don't instead of embedding a broken image. Slower but safer.
  VERIFY_URLS_BEFORE_EMBED: true,

  CHARACTER_TABLE_URL:
    "https://raw.githubusercontent.com/TacticalBreakfast/ArknightsGuideAssets/main/excel-cn/character_table.json",
  UNIEQUIP_TABLE_URL:
    "https://raw.githubusercontent.com/TacticalBreakfast/ArknightsGuideAssets/main/excel-en/uniequip_table.json",
  IMAGE_BASE_URL:
    "https://raw.githubusercontent.com/TacticalBreakfast/ArknightsGuideAssets/main",
};

function embedOperatorImages() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) {
    throw new Error(`Sheet tab "${CONFIG.SHEET_NAME}" not found. Check CONFIG.SHEET_NAME.`);
  }

  const byAppellation = buildAppellationMap_(loadCharacterTable_());
  const subProfDict = CONFIG.SET_SUBCLASS_INFO ? loadUniequipSubProfDict_() : {};

  const lastRow = sheet.getLastRow();
  const notFound = [];
  const brokenImages = [];
  const dividersSkipped = [];
  const rarityIssues = [];
  const unresolvedSubclasses = [];
  let embeddedCount = 0;
  let operatorCount = 0;

  let nameRow = CONFIG.START_ROW;
  while (nameRow <= lastRow) {
    const name = String(sheet.getRange(nameRow, 1).getValue()).trim();
    if (!name) break; // ran off the end of the operator blocks

    operatorCount++;
    const match = byAppellation[name];
    if (!match) {
      notFound.push(`Row ${nameRow}: "${name}"`);
    } else {
      if (CONFIG.EMBED_PORTRAITS) {
        const portraitRow = nameRow + CONFIG.PORTRAIT_ROW_OFFSET;
        const url = `${CONFIG.IMAGE_BASE_URL}/charavatars/${match.id}.png`;
        if (embedImage_(sheet, portraitRow, CONFIG.PORTRAIT_COL_START, url, `${name} portrait`, brokenImages)) {
          embeddedCount++;
        }
      }

      if (CONFIG.SET_RARITY_STYLING) {
        applyRarityStyling_(sheet, nameRow, name, match.rarity, rarityIssues);
      }

      if (CONFIG.SET_SUBCLASS_INFO) {
        if (
          applySubclassInfo_(
            sheet,
            nameRow,
            name,
            match.subProfessionId,
            subProfDict,
            brokenImages,
            unresolvedSubclasses
          )
        ) {
          embeddedCount++;
        }
      }
    }

    // e.g. "char_2027_wang" -> "wang"; "char_1050_chen3" -> "chen3"
    const shortName = match ? match.id.split("_").slice(2).join("_") : null;

    // Walk down one row per skill, keyed off the existing "S#M#" label in
    // SKILL_LABEL_COL rather than the operator's total skill count in
    // character_table.json — a guide only documents the skills worth
    // discussing (e.g. Ju's guide only covers S2, even though he has 2
    // skills in-game), so the sheet's own labels are the source of truth
    // for which skill rows actually exist here.
    let skillRow = nameRow + CONFIG.SKILL_ROW_OFFSET;
    while (skillRow <= lastRow) {
      const label = String(sheet.getRange(skillRow, CONFIG.SKILL_LABEL_COL).getValue()).trim();
      const labelMatch = /^S(\d+)/i.exec(label);
      if (!labelMatch) break;

      if (shortName) {
        const skillNum = parseInt(labelMatch[1], 10);
        const url = `${CONFIG.IMAGE_BASE_URL}/skills/skill_icon_skchr_${shortName}_${skillNum}.png`;
        if (embedImage_(sheet, skillRow, CONFIG.SKILL_ICON_COL, url, `${name} S${skillNum} icon`, brokenImages)) {
          embeddedCount++;
        }
      }
      skillRow++;
    }

    nameRow = findNextOperatorRow_(sheet, skillRow, lastRow, dividersSkipped);
    if (nameRow === null) break;
  }

  report_(operatorCount, embeddedCount, notFound, brokenImages, dividersSkipped, rarityIssues, unresolvedSubclasses);
}

/**
 * Starting just after the current operator's skill row, scans downward for
 * a row that's blank across all NAME_COL_SPAN columns, then returns the
 * first non-blank row after it (the next operator's name row). If that row
 * turns out to be a section divider (its text matches SECTION_DIVIDER_TEXTS),
 * it's recorded and skipped, and the scan resumes for the next blank+non-
 * blank sequence — so a blank/divider/blank run is passed over entirely.
 * Returns null if no further operator block is found.
 */
function findNextOperatorRow_(sheet, fromRow, lastRow, dividersSkipped) {
  let row = fromRow;
  while (row !== null) {
    row = findNextNonBlankAfterBlank_(sheet, row, lastRow);
    if (row === null) return null;

    const text = String(sheet.getRange(row, 1).getValue()).trim();
    if (isSectionDivider_(text)) {
      dividersSkipped.push(`Row ${row}: "${text}"`);
      row = row + 1;
      continue;
    }
    return row;
  }
  return null;
}

function findNextNonBlankAfterBlank_(sheet, fromRow, lastRow) {
  let row = fromRow;
  let blankFound = false;
  while (row <= lastRow) {
    const rowValues = sheet.getRange(row, 1, 1, CONFIG.NAME_COL_SPAN).getValues()[0];
    const isBlank = rowValues.every((v) => String(v).trim() === "");
    if (isBlank) {
      blankFound = true;
    } else if (blankFound) {
      return row;
    }
    row++;
  }
  return null;
}

function isSectionDivider_(text) {
  const normalized = text.trim().toLowerCase();
  return CONFIG.SECTION_DIVIDER_TEXTS.some((d) => d.trim().toLowerCase() === normalized);
}

function buildAppellationMap_(charTable) {
  const byAppellation = {};
  for (const id in charTable) {
    const entry = charTable[id];
    byAppellation[entry.appellation] = {
      id: id,
      rarity: entry.rarity,
      subProfessionId: entry.subProfessionId,
    };
  }
  return byAppellation;
}

function parseRarityNumber_(rarityStr) {
  const m = /TIER_(\d+)/i.exec(String(rarityStr || ""));
  return m ? parseInt(m[1], 10) : null;
}

function loadCharacterTable_() {
  const resp = UrlFetchApp.fetch(CONFIG.CHARACTER_TABLE_URL, { muteHttpExceptions: true });
  if (resp.getResponseCode() !== 200) {
    throw new Error(`Failed to fetch character_table.json: HTTP ${resp.getResponseCode()}`);
  }
  return JSON.parse(resp.getContentText());
}

function loadUniequipSubProfDict_() {
  const resp = UrlFetchApp.fetch(CONFIG.UNIEQUIP_TABLE_URL, { muteHttpExceptions: true });
  if (resp.getResponseCode() !== 200) {
    throw new Error(`Failed to fetch uniequip_table.json: HTTP ${resp.getResponseCode()}`);
  }
  return JSON.parse(resp.getContentText()).subProfDict || {};
}

function embedImage_(sheet, row, col, url, label, brokenImages) {
  if (CONFIG.VERIFY_URLS_BEFORE_EMBED) {
    const resp = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    if (resp.getResponseCode() !== 200) {
      brokenImages.push(`${label}: HTTP ${resp.getResponseCode()} — ${url}`);
      return false;
    }
  }
  const image = SpreadsheetApp.newCellImage().setSourceUrl(url).setAltTextTitle(label).build();
  sheet.getRange(row, col).setValue(image);
  return true;
}

/**
 * Writes the rarity as ★ characters into the star cell (same row as the
 * top of the portrait, STAR_COL_START), and colors both that cell and the
 * name row's top-left cell according to RARITY_COLORS.
 */
function applyRarityStyling_(sheet, nameRow, name, rarityStr, rarityIssues) {
  const rarityNum = parseRarityNumber_(rarityStr);
  if (rarityNum === null) {
    rarityIssues.push(`Row ${nameRow}: "${name}" has an unrecognized rarity "${rarityStr}"`);
    return;
  }

  const starRow = nameRow + CONFIG.PORTRAIT_ROW_OFFSET;
  const starCell = sheet.getRange(starRow, CONFIG.STAR_COL_START);
  starCell.setValue("★".repeat(rarityNum));

  const color = CONFIG.RARITY_COLORS[rarityNum];
  if (!color) {
    rarityIssues.push(`Row ${nameRow}: "${name}" has rarity ${rarityNum} with no entry in RARITY_COLORS`);
    return;
  }
  starCell.setFontColor(color);
  sheet.getRange(nameRow, 1).setFontColor(color);
}

/**
 * Writes the English subclass name into the cell directly below the stars,
 * falling back to "TBD" if uniequip_table.json has no translation for this
 * subProfessionId yet, and embeds the subclass icon at (star row,
 * SUBCLASS_ICON_COL_START). Returns whether the icon embed succeeded.
 */
function applySubclassInfo_(sheet, nameRow, name, subProfessionId, subProfDict, brokenImages, unresolvedSubclasses) {
  const starRow = nameRow + CONFIG.PORTRAIT_ROW_OFFSET;
  const subclassNameRow = starRow + 1;

  const subProfEntry = subProfDict[subProfessionId];
  const subclassName = subProfEntry && subProfEntry.subProfessionName ? subProfEntry.subProfessionName : "TBD";
  if (subclassName === "TBD") {
    unresolvedSubclasses.push(
      `Row ${nameRow}: "${name}" has no English subclass name for subProfessionId "${subProfessionId}"`
    );
  }
  sheet.getRange(subclassNameRow, CONFIG.STAR_COL_START).setValue(subclassName);

  const iconUrl = `${CONFIG.IMAGE_BASE_URL}/subprofessionicon/sub_${subProfessionId}_icon.png`;
  return embedImage_(sheet, starRow, CONFIG.SUBCLASS_ICON_COL_START, iconUrl, `${name} subclass icon`, brokenImages);
}

function report_(
  operatorCount,
  embeddedCount,
  notFound,
  brokenImages,
  dividersSkipped,
  rarityIssues,
  unresolvedSubclasses
) {
  const lines = [`Scanned ${operatorCount} operator block(s), embedded ${embeddedCount} image(s).`];

  if (dividersSkipped.length) {
    lines.push("", `Skipped ${dividersSkipped.length} section divider(s):`);
    dividersSkipped.forEach((l) => lines.push(`  - ${l}`));
  }

  if (rarityIssues.length) {
    lines.push("", `RARITY STYLING ISSUES (${rarityIssues.length}) — need addressing:`);
    rarityIssues.forEach((l) => lines.push(`  - ${l}`));
  }

  if (unresolvedSubclasses.length) {
    lines.push(
      "",
      `SUBCLASS NAME SET TO "TBD" (${unresolvedSubclasses.length}) — no English translation ` +
        `in uniequip_table.json yet, needs addressing once one exists:`
    );
    unresolvedSubclasses.forEach((l) => lines.push(`  - ${l}`));
  }

  if (notFound.length) {
    lines.push(
      "",
      `OPERATOR NOT FOUND (${notFound.length}) — name in sheet doesn't match any ` +
        `appellation in character_table.json. Check for typos, or the operator may ` +
        `not be in the game data yet:`
    );
    notFound.forEach((l) => lines.push(`  - ${l}`));
  }

  if (brokenImages.length) {
    lines.push(
      "",
      `IMAGES NOT EMBEDDED (${brokenImages.length}) — URL did not return a valid ` +
        `image, these need addressing:`
    );
    brokenImages.forEach((l) => lines.push(`  - ${l}`));
  }

  lines.push("", "REMINDER: manually update the links and gacha pools.");

  const message = lines.join("\n");
  Logger.log(message);

  try {
    SpreadsheetApp.getUi().alert(
      notFound.length || brokenImages.length || rarityIssues.length || unresolvedSubclasses.length
        ? "Image embed finished with issues"
        : "Image embed finished",
      message,
      SpreadsheetApp.getUi().ButtonSet.OK
    );
  } catch (e) {
    // getUi() throws when there's no active spreadsheet UI context (e.g. run
    // from a trigger). The Logger.log call above already has the full report.
  }
}
