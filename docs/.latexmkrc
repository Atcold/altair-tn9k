$pdf_mode = 4;                                   # lualatex
$out_dir = 'build';
@default_files = ('*.tex');
do './revision.pl';                              # the revision line, from git
