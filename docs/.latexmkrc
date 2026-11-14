$pdf_mode = 4;                                   # lualatex
$out_dir = 'build';
@default_files = ('*.tex');
# alfdoc, the shared style (github.com/Atcold/alfdoc): through ~/Library/texmf when it is linked
# there, otherwise cloned into build/ on the first build. Then its revision line, from git.
my $alfdoc = `kpsewhich alfdoc.sty` =~ s{/alfdoc\.sty\s*$}{}r;
if ($alfdoc eq '') {
  $alfdoc = "$out_dir/alfdoc";
  system('git', 'clone', '-q', '--depth=1', 'https://github.com/Atcold/alfdoc', $alfdoc) unless -d $alfdoc;
  ensure_path('TEXINPUTS', "$alfdoc//");
}
do "$alfdoc/revision.pl";
