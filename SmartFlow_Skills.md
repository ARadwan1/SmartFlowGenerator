# Smart Flow Advanced Language - AI Generation Skills Guide

This document serves as the foundation for building an application/AI agent that generates Amadeus Smart Flows from natural language user definitions. It contains the syntax, structure, and best practices for writing Smart Flow Advanced Language scripts based on official Amadeus documentation and real-world examples.

## Next Steps for the Smart Flow Generator Application
1. Implement an AI prompt template using this MD file as the precise context for the LLM.
2. Build a user interface where agents/administrators can describe the desired Smart Flow in natural language.
3. Validate generated scripts against the rules and syntax provided below before allowing users to save or run them.

---

## 1. Syntax Basics & Variables
Smart Flow scripts run sequentially. The language uses basic scripting logic. 

**CRITICAL:** Smart Flow does NOT support internal mathematical operations. The `+` operator is used ONLY for string concatenation (e.g., `"5" + "2"` evaluates to `"52"`). To calculate values, you must send an Amadeus calculator command (like `DF`) and then `capture` the result from the screen.

**Variables:**
- Variables act as containers to store data (e.g., `firstName`, `paxNo`).
- Variables are assigned using `assign to <variableName>`.
- **System Variables:**
  - `commandline`: Used with `append` to build a cryptic command string.
  - `lastCommand`: Stores the cryptic command that triggered the flow.
  - `today`: Contains today's date in `DDMMM` format.
- Concatenation is done using the `+` operator (e.g., `"NM1" + lastName + "/" + firstName`).

## 2. Statements & Commands

### `send`
Executes cryptic commands to the Amadeus system.
```smartflow
send "RT"
send "NM1" + lastName + "/" + firstName
send commandline
```

### `ask` / User Input Prompts
Prompts user to enter free text or formatted content. Always uses `assign to`.
Can be preceded by `mandatory` to force input.

**Variants:**
- `ask "Question?" assign to varName`
- `mandatory ask "Question?" assign to varName`
- `ask date "Date?" assign to varName`
- `ask date "Date?" with format DDMON assign to varName` (Supported: DDMM, DDMMYY, DDMON, DDMONYY, DDMONYYYY, MMYY)
- `ask email "Email?" assign to varName`
- `ask number "Number?" assign to varName`
- `ask "Question?" with format "^[a-zA-Z]{2,3}$" assign to varName` (Regex support)

### `select`
Creates a dropdown menu of predefined options.
```smartflow
select "Select Document Type" from "Passport (P),Identity card (A),Other" assign to DocType
```

### `choose`
Creates a series of radio buttons or menu choices. Each choice triggers a specific block of code `when("...")`.
```smartflow
choose "Is this passenger the main document holder?" {
    when ("Yes") {
        append "H" to Holder
    }
    when ("No") {
        append "" to Holder
    }
}
```

### `choose until` / `ask until`
Loops a menu until the user selects the exit condition.
```smartflow
choose "Add more sectors or Exit" until "Exit" {
    when ("Add sector") {
        // ... ask for details and append
    }
}
```

### `group`
Groups multiple `ask` or `select` statements into a single form popup.
```smartflow
group {
    mandatory ask "Family Name" assign to lastName
    mandatory ask "First Name" assign to firstName
    ask date "Date of Birth" with format DDMONYY assign to dob
}
```

### `capture`
Reads data from the terminal screen (Command Page) at specific coordinates.
```smartflow
// Syntax: capture line : X, column : Y, length : Z assign to varName
capture line : 2, column : 32, length : 2 assign to Seats
```

### `if` / `else`
Conditional logic (supported operators: `==`, `!=`, `>`, `<`).
**CRITICAL:** The language does NOT support `else if`. To chain conditions, you MUST use nested `if` statements inside an `else` block.
```smartflow
if (Seats > 1) {
    send "APN-SV/M+" + PhoneNo + "/P1-" + Seats
} else {
    send "APN-SV/M+" + PhoneNo + "/P1"
}
```

### `append`
Adds text or variables to a string (often to `commandline` or another string variable).
```smartflow
append "INT" to SI
append "/T" + ADTime to commandline
```

### `call`
Invokes another nested Smart Flow by name.
**CRITICAL:** When constructing a `commandline` string across multiple steps, if a `call` is invoked and there are no further appends before the final `send commandline`, you MUST explicitly `append "" to commandline` right after the `call` to ensure the buffer is correctly pushed.
```smartflow
call "Names, DOCS and Contact"
```

### `//` (Comments)
Used for inline comments.
```smartflow
// This is a comment
```

## 3. Advanced UI / HTML Formatting
Smart Flows support HTML tags within question labels to style text. 
Common patterns:
- `<h1 style = color:#D40B0B>Red Title</h1>`
- `<b>Bold Text</b>`
- `<i>Italic Text</i>`
- `<p style=font-size:0.6vw>`

**Example:**
```smartflow
mandatory ask "<h1 style = color:#D40B0B>Passenger information</h1>
Family Name (surname)" assign to FamilyName
```

## 4. Best Practices for Generated Code
1. **Validation & State:** Use `capture` heavily to parse existing PNR states (e.g., capturing the number of seats or finding a specific element line number) before executing subsequent steps.
2. **Error Handling/Looping checks:** Ensure that variables captured from the screen do not lead to invalid executions. (e.g., checking if `Seats != ""`).
3. **Data Security:** Never store credit cards or sensitive parameters permanently in the script.
4. **Modularity:** Group long data entry forms into `group { ... }` blocks to improve agent usability. Use `choose` workflows to segment complex steps (like adding an infant vs. adding DOCS only).
5. **Automation over Manual Input (The Golden Standard):** When data positions on the screen are dynamic, ALWAYS prioritize automation via "Fallback Capturing" (nesting `if/else` checks to scan down the screen) rather than relying on static coordinates or asking the user for the line number. Only use manual prompting as a last resort if programmatic verification is completely impossible.

## 5. Advanced Logic Patterns (From Real-World Scripts)

### A. "Looping" via Nested IF Statements & UI Loops
Smart Flow does not have a native `for` or `while` loop syntax for background array processing. To automatically scrape or parse dynamic amounts of terminal data without user intervention, you MUST use nested `if` statements (e.g., Fallback Capturing). 
However, for user-driven input aggregation (prompting the user an unknown number of times), use the native UI loop: `choose ... until ...`. Do NOT attempt to build custom background programming loops.

**Example (Processing up to 3 tickets):**
```smartflow
select "Count Of Documents" from "1,2,3" assign to varNumberOfDocument 

if (varNumberOfDocument != "1"){
    if (varNumberOfDocument != "2"){
        group {
           mandatory ask "Document 3: Enter the next document number" assign to varDocumentNumber3
        }
    }
}
```

### B. Fallback Capturing (Checking multiple lines for an element)
When an Amadeus terminal element (like `FO` Original Issue, or `FARE FAMILIES`) could appear on multiple different lines depending on the PNR size, you must nest `if/else` captures to scan down the screen.

**Example (Hunting for an FO line):**
```smartflow
capture line : 10, column : 1, length : 7 assign to FoPos
if (FoPos == "FO 065-"){
    capture line : 10, column : 8, length : 34 assign to FoString
} else {
    capture line : 11, column : 1, length : 7 assign to FoPos
    if (FoPos == "FO 065-"){
        capture line : 11, column : 8, length : 34 assign to FoString
    } else {
        // ... continue nesting down to line 20+
    }
}
```

### C. Advanced UI Formatting & Validation
- **Regex Validation:** You can force specific input formats using `with format`.
  `mandatory ask "Passport issuance country" with format "^[a-zA-Z]{2,3}$" assign to DocIssCou`
- **Warnings/Alerts:** Use HTML to mimic system warnings inside `choose` blocks.
  ```smartflow
  choose "<b style=color:#D40B0B>*** BE SURE TO BOOK SEGMENT FOR 2 SEATS FIRST ***</b>" {
      when ("OK") {}
  }
  ```

## 6. Terminal Coordinates & Capture Mappings (Amadeus Cryptic)
Because Smart Flow heavily relies on screen scraping via `capture line : X, column : Y, length : Z assign to varName`, understanding the exact layout of Amadeus responses is critical. 

Below are common capture coordinates based on standard Amadeus cryptic responses.

### A. PNR Display (RT)
PNR Headers often contain the Record Locator and Creating Office.
- **Record Locator:** Usually Line 2, Column 54-55 (Length 6). (e.g., `8QOCED` in `RP/DMMSV0101/...  8QOCED`)
- **Passenger Names:** Start on Line 3. Format is usually `1.LAST/FIRST TITLE(PTC)`. 
- **Segments:** Usually follow names. Look for status codes like `HK`, `HL`, `TK`. 
- **FA Elements (Tickets):** Format `FA PAX 065-1234567890/ETSV/SAR446.20/...`. Often captured to find ticket numbers or total amounts.

*Note: PNR structures vary greatly based on the number of passengers and elements. Scripts usually need to prompt the user for the specific line number to capture from, or use a loop/Smart Flow logic if available.*

### B. Ticket Image (TWD)
The `TWD` screen shows exact ticketing details.
**CRITICAL RULES FOR TWD:**
1. **Command Syntax:** To open a ticket image, you MUST use `TWD/TKT` (NOT `TWD/T`). Example: `send "TWD/TKT" + TicketNumber`.
2. **Ticket Hyphen:** The input ticket number MUST contain a hyphen after the airline code to prevent failure (e.g., `065-1234567890`). Ensure prompts or regex enforce the hyphen.
3. **Dynamic Totals:** DO NOT use static line tracking (like line 9) for `TOTAL `. You MUST use Fallback Capturing (nested `if/else` from line 5 to 20+) to search for the word `TOTAL ` and then capture the amount that follows the currency code (e.g. `SAR`).

- **Ticket Number:** Line 1, Column 5, Length 13. (e.g., `0652194446737` from `TKT-0652194446737`)
- **Issue Date (DOI):** Line 2, Column 38, Length 7. (e.g., `23FEB26` from `DOI-23FEB26`)
- **Original Issue (FO):** If reissued, the original ticket details appear as an `FO` line near the bottom.

### C. EMD Image (EWD)
The `EWD` screen is used for ancillary services (bags, seats, penalties).
- **EMD Number:** Line 1, Column 5, Length 13. (e.g., `0654226691263`)
- **Passenger Name:** Line 3, Column 6, Length varies. (e.g., `ALAJMI/FATEMAH`)
- **Value (Base):** Line 11, Column 22, Length 8. (e.g., `1792.86` from `FARE   R    SAR        1792.86`)
- **Total Price:** Line 14, Column 22, Length 8. (Or `NO ADC` for zero-value reissues).

### D. Fare/Price Display (FXP / FXB)
Pricing displays show totals and fare families.
- **Totals Line:** Look for `TOTALS`. The total passenger count, base fare, tax, and absolute total are listed here. (e.g., `                   TOTALS    3     846.00  558.15    1404.15`)
- **Upsell info:** Shows fare families (e.g., `NSAVERE`, `NBASICE`).

### E. Display Fares (DF) / Calculator
The `DF` command in Amadeus is used as an inline calculator.
- Output always appears exactly on the **second line** after the command.
- Use `capture line : 2, column : 1, length : 9 assign to varName` to grab the calculation result.
- Example: 
  `send "df" + var1 + "-" + var2`
  `capture line : 2, column : 1, length : 9 assign to Difference`

### F. Informative Pricing (FQP)
The `FQP` command prices an itinerary **without** creating a PNR. This is the primary tool for fare quoting.

**Basic Syntax:** `FQP` followed by city pairs (3-letter IATA codes concatenated).
```
FQP MADNYC          // One-way Madrid to New York
FQP LONSINLON       // Return London-Singapore-London
FQP LONBOMSYDTYOFRA // Multi-city
```

**Segment-Level Options** (placed BETWEEN city codes):

| Option | Meaning | Example |
|--------|---------|---------|
| `/A XX` | Specific airline for segment | `FQP LON/ABASINJKT/ASQBKK` |
| `/D DDMON` | Travel date | `FQP LON/D04SEPSIN/D18OCTLON` |
| `/C X` | Booking code (RBD) | `FQP LON/CFSIN/CYLON` |
| `/B` | Fare breakpoint | `FQP LON/BPARHEL` |
| `/N` | Prohibit breakpoint | `FQP LAX/NTYOSEL` |
| `/T` | Turnaround point | `FQP LON/TPARHEL` |
| `/V XX` | Global route indicator | `FQP LON/VEHSINLON` |
| `/H HHMM` | Night fares | `FQP MAD/H2305LPA` |
| `/E XXX` | Aircraft/equipment type | `FQP NCE/AIO/CC/ES58MCM` |
| `-` | Stopover indicator | `FQP MADGVACPH-FRAZRHBUD` |
| `--` | Surface sector | `FQP REKLON--FRAATH` |
| `---` | Stopover + surface | `FQP LONFRAHAM---MUCDUSLON` |

**Itinerary-Level Options** (placed at END of entry):

| Option | Meaning | Example |
|--------|---------|---------|
| `/O XX` | Same airline all segments | `FQP NCEPARMIAPARNCE/OAF` |
| `/M` | Mirror image (return = reverse of outbound) | `FQP LONSIN/M` |
| `/L` | Lowest priced ticket image | `FQP MIALON/L` |
| `/S` | Display mask only | `FQP LONSINLON/S` |
| `/P` | Display fares + mask | `FQP LONSIN/P` |
| `/R ZZ` | Passenger discount | `FQP LON/ABAPARLON/RZZ` |
| `/R MIL` | Passenger type code | `FQP LAX/AYXNYC/RMIL` |
| `/R MIL,*PTC` | PTC only (no lower fares) | `FQP LAX/AYXNYC/RMIL,*PTC` |
| `/R,LON` | Point of sale override | `FQP MADPARMAD/R,LON` |
| `/R,.FRA` | Ticketing city override | `FQP MADPARMAD/R,.FRA` |
| `/R,OCC-6X` | Controlling carrier override | `FQP AKL/A6XMEL/A7XKUL/R,OCC-6X` |
| `/R,FC-USD` | Currency of sale override | `FQP LONSIN/R,FC-USD` |
| `/R,IATA` | Rules source override | `FQP PARABJPAR/R,IATA` |
| `/R,ET` | Tax exemption | `FQP LONNCELON/R,ET` |
| `/R,WT` | Withhold all taxes | `FQP LONNCELON/R,WT` |
| `/R,WQ` | Withhold surcharges | `FQP NYC/AAARIO/R,WQ` |
| `/R,AC-XX` | Add taxes by country | `FQP BOG/ACOMIA-EWR-BOG/R,AC-US` |
| `/R,WC-XX` | Withhold taxes by country | `FQP PAR/AAFFRA-LON-PAR/R,WC-DE` |

**Fare Families:** Use `/FF-NAME` for full itinerary or `/FF1-NAME/FF2-NAME` per segment:
```
FQP MAD/A6X/CYPAR/A6X/CELON/R,UP/FF-ECO
FQP MAD/A6X/CYPAR/A6X/CELON/R,UP/FF1-ECO/FF2-CLASSIC
```

**Fare Combinations (FQU):** Sum fares from an FQP display:
```
FQU1//2//3            // Add fare lines 1, 2, and 3
FQU1/X2//2/X3//3/X4   // Multiply: 2 adults, 3 children, 4 infants
```

**Multiple Discounts:** Up to 6 codes separated by `*`: `/RCH*ZZ*IN*ADT`

**Expanded Parameter Codes:**

| Code | Meaning |
|------|---------|
| `NAP` | No advance purchase info |
| `NDA` | No day/time info |
| `NMX` | No maximum stay info |
| `NMN` | No minimum stay info |
| `NPE` | No penalty info |
| `PE` | Penalty info |
| `NR` | No restriction |
| `RF` | Refundable |
| `NRF` | Non-refundable |

Example: `FQP NYC/AAAMIABOS/R,*NPE-NAP`

**FQP Response Columns:**
- `FARE BASIS` – The fare basis code
- `DISC` – Discount applied (blank if none)
- `PTC` – Passenger type (1=Adult, or discount number)
- `FARE<CUR>` – Fare amount in local currency (includes airline ticketing fees)
- `MSG` – Messages: `FL`=flight restriction, `FQ`=no flights on date, `RB`=check booking code, `RE`=reservation conditions, `RO`=higher class required, `SR`=sales restrictions
- `T` – Tax indicator: `Y`=included, `N`=not included, `E`=exempt

**Past Date Pricing:** `FQP MUCPAR/R,15FEB05` (up to 24 months in the past, authorized users only)

**CRITICAL FOR SMART FLOW GENERATION:**
1. When building an FQP command dynamically, use `append` to construct `commandline` piece by piece: first the city pairs, then segment options, then itinerary options.
2. Airline codes follow `/A` immediately with NO space: `/ABA` not `/A BA`.
3. Dates follow `/D` immediately: `/D04SEP` not `/D 04SEP`.
4. Multiple options can be chained: `FQP LON/D14SEP/ABA/CF/VEHSIN/D18OCT/ASQ/CY/VEHLON/RCH,PAR.MAD`
5. The `TOTALS` line in FQU responses is dynamic. Use Fallback Capturing to find it.
