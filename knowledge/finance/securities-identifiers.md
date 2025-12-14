# Securities Identifiers - ISIN, CUSIP, SEDOL

## ISIN (International Securities Identification Number)

### What is ISIN?
- 12-character alphanumeric code
- Unique identifier for securities (stocks, bonds, derivatives)
- International standard (ISO 6166)

### Structure
```
[Country Code (2)] + [NSIN (9)] + [Check Digit (1)]

Example: US0378331005 (Apple Inc.)
- US = United States
- 037833100 = National Securities Identifying Number
- 5 = Check digit (Luhn algorithm)
```

### Key Points
- Used globally for cross-border trading
- Assigned by National Numbering Agencies (NNAs)
- In US, CUSIP Service Bureau assigns
- In India, NSDL assigns

---

## CUSIP (Committee on Uniform Securities Identification Procedures)

### What is CUSIP?
- 9-character alphanumeric code
- Used in US and Canada
- Identifies securities for trading and settlement

### Structure
```
[Issuer (6)] + [Issue (2)] + [Check Digit (1)]

Example: 037833100 (Apple Inc.)
- 037833 = Issuer number (Apple)
- 10 = Issue number (common stock)
- 0 = Check digit
```

### Types
- **CUSIP-6**: First 6 characters (issuer identifier)
- **CUSIP-9**: Full 9 characters (specific security)
- **CINS**: CUSIP International Numbering System (for non-US securities)

---

## SEDOL (Stock Exchange Daily Official List)

### What is SEDOL?
- 7-character alphanumeric code
- Used in UK and Ireland
- Assigned by London Stock Exchange

### Structure
```
[Alphanumeric (6)] + [Check Digit (1)]

Example: B1YW440 (Barclays)
```

---

## Comparison Table

| Feature | ISIN | CUSIP | SEDOL |
|---------|------|-------|-------|
| Length | 12 | 9 | 7 |
| Scope | Global | US/Canada | UK/Ireland |
| Prefix | Country code | Issuer | None |
| Standard | ISO 6166 | ANSI X9.6 | LSE |

---

## Quiz Questions

1. How many characters are in an ISIN?
2. What do the first two characters of ISIN represent?
3. What's the difference between CUSIP-6 and CUSIP-9?
4. Which identifier is used globally for cross-border trading?
5. Apple's CUSIP is 037833100. What is its ISIN?
