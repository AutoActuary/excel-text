# excel-text

Python implementation of Excel's `text` function.

The 1900 bug is reproduced.

## Upstream docs

- https://support.microsoft.com/en-us/office/text-function-20d5ac4d-7b94-49fd-bb38-93d29371225c
- https://docs.microsoft.com/en-us/office/troubleshoot/excel/wrongly-assumes-1900-is-leap-year
- https://www.quora.com/Why-wont-Microsoft-fix-the-1900-leap-year-bug-that-exists-in-Excel

## Examples

1. Currency with thousands separators and decimals. 
   `=TEXT(1234.567,"$#,##0.00")` = `$1,234.57`
2. Date and time functions.
   `=TEXT(10,"MM/DD/YYYY")` = `01/10/1900`
3. Percentages
   `=TEXT(0.285,"0.0%")` = `28.5%`
4. Leading zeros
   `=TEXT(1234,"0000000")` = `0001234`
5. Custom Latitude/longitude
   `=TEXT(123456,"##0° 00' 00''")` = `12° 34' 56''`

## Limitations

- Filling with `*` is not supported.
- `@` is not supported in the format argument.
- Single quotation marks `'` are not supported for inserting strings. Double quotation marks `"` must be used.
- String characters that can be incorrectly interpreted as datetime options can only be used if used with quotation 
marks. 
- When `[]` are used for date/datetime/time, only the first character in the brackets will be used.

