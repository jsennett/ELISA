How to write ELISA Assembly Instructions

- labels must be specified on their own line, and cannot be instruction mnemonics.
- sections are `.data` and `.text`. Text sections come first, and data sections come second. If no .text section is specified, it is implied at the top of the file. If no .data section is specified, there is assumed to be no data loaded into the program.

label_name:

