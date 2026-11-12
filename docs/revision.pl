# Revision line and table from git, for alfdoc. A lesson's .latexmkrc runs it with
#   do '../style/revision.pl';
# and any other document's with
#   do "$ENV{HOME}/Library/texmf/tex/latex/alfdoc/revision.pl";
# (or the copy a public repo ships next to its alfdoc.sty) after setting $out_dir.
# With $jobname set, as in a lesson, the main document's <jobname>.rev comes from every commit that
# touched the folder, and another document X.tex there, built with -jobname=<folder>-X, gets
# <folder>-X.rev from the commits that touched X.tex alone. Without $jobname, as in a folder of
# reports, every document X.tex gets X.rev from its own commits. Each .rev holds the revision
# number, the date and short hash of the last commit, and one row per commit, each hash with its
# GitHub link. Uncommitted changes make the next revision, a draft dated today on top of it.
use Cwd ();

my $folder = (split m{/}, Cwd::getcwd())[-1];
my $dir = $out_dir || '.';

# GitHub page of the repo, so each hash in the table links to its diff
my $web = `git remote get-url origin 2>/dev/null`;
chomp $web;
$web =~ s{^git\@github\.com:}{https://github.com/};
$web =~ s{\.git$}{};
$web = '' unless $web =~ m{^https://github\.com/};

sub alfdoc_rev {
  my ($name, $path) = @_;
  my $count = `git rev-list --count HEAD -- '$path' 2>/dev/null`;
  chomp $count;
  return if $count eq '';  # not in a git repo
  my $last = `git log -1 --format='%h|%cd' --date=format:'%a %-d %b %Y' -- '$path'`;
  chomp $last;
  my ($hash, $date) = split /\|/, $last;
  $hash //= '';  # a new file has no commit yet
  my $draft = `git status --porcelain -- '$path'` ne '' ? 1 : 0;
  return unless $count or $draft;
  if ($draft) {
    $count += 1;
    my @t = localtime;
    my @day = qw(Sun Mon Tue Wed Thu Fri Sat);
    my @mon = qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec);
    $date = sprintf '%s %d %s %d', $day[$t[6]], $t[3], $mon[$t[4]], $t[5] + 1900;
  }
  mkdir $dir;
  open my $fh, '>', "$dir/$name.rev" or die "revision.pl: $!";
  print $fh "\\alfdoc\@revision{$count}{$date}{$hash}{$draft}\n";
  # Date cells: weekday, day, month and year. A value that repeats the row above is \alfdoc@same,
  # light grey: the month and year alone, the weekday and day only with the whole date.
  my ($prev_day, $prev_month) = ('', '');
  my $cells = sub {
    my ($wd, $dd, $my) = split / /, $_[0], 3;
    my $same_day = "$wd $dd $my" eq $prev_day;
    my $out = join ' & ', ($same_day ? ("\\alfdoc\@same{$wd}", "\\alfdoc\@same{$dd}") : ($wd, $dd)),
      ($my eq $prev_month ? "\\alfdoc\@same{$my}" : $my);
    ($prev_day, $prev_month) = ("$wd $dd $my", $my);
    return $out;
  };
  my @log = reverse split /\n/,
    `git log --format='%h|%cd|%s' --date=format:'%a %-d %b %Y' -- '$path'`;
  my $n = 0;
  for (@log) {
    my ($h, $d, $s) = split /\|/, $_, 3;
    # Review: “It's useless having working-with-claude: in the subject. I already commit one
    # lesson at a time, so it's just wasting space.”
    $s =~ s/^\Q$folder\E: //i;  # the table is this folder's already
    $s =~ s/^\Q$name\E: //i;    # or this document's
    $s =~ s/([\\{}])/\\char`\\$1/g;  # backslash and braces first, as characters
    $s =~ s/([&%\$#_])/\\$1/g;
    $s =~ s/~/\\textasciitilde{}/g;
    $s =~ s/\^/\\textasciicircum{}/g;
    $n++;
    print $fh "\\alfdoc\@revrow{$n}{" . $cells->($d) . "}{$h}{$s}\n";
    print $fh "\\alfdoc\@commiturl{$h}{$web/commit/$h}\n" if $web;
  }
  print $fh "\\alfdoc\@revrow{$count}{" . $cells->($date) . "}{}{Uncommitted changes, this draft}\n" if $draft;
  close $fh;
}

# Every document in the folder: a file whose source starts a LaTeX document
my @docs;
for my $tex (glob '*.tex') {
  my $source = do { local $/; open my $in, '<', $tex or next; <$in> };  # $/ local to this read
  push @docs, $tex if $source =~ /^\\documentclass/m;
}
if ($jobname) {
  # A lesson: the main document has the whole folder, every other one its own file
  my %is_main = map { $_ => 1 } @default_files;
  alfdoc_rev($jobname, '.');
  alfdoc_rev("$folder-" . ($_ =~ s/\.tex$//r), $_) for grep { !$is_main{$_} } @docs;
} else {
  # A folder of reports: each its own file
  alfdoc_rev($_ =~ s/\.tex$//r, $_) for @docs;
}
1;
