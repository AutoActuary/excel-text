# excel-text
Python implementation of the excel text function.

Current functional formulas:
1) Currency with a thousands seperator and with decimals. 
E.g =TEXT(1234.567,"$#,##0.00") = $1,234.57
2) Datetime/Date/time functions.
E.g. =TEXT(10,"MM/DD/YYYY") = 01/10/1900
3) Percentage
E.g. =TEXT(0.285,"0.0%") = 28.5%
4) Add leading zeros
E.g. =TEXT(1234,"0000000") = 0001234
5) Custom Latitude/longitude
E.g. =TEXT(123456,"##0° 00' 00''") = 12° 34' 56''


Filling (*) is not supported in this function.

Single quotation marks ('') are not supported to insert a string into the function. Double quotation marks must be 
used ("").

String characters that can wrongfully be interepreted as datatime options, can only be used if used with quotation 
marks. 

When [] are used, only the first character in the brackets will be used.

\ ; @ are not supported.