%%% ====================================================================
%%%  Modified from hamsplain.bst for natbib-compatible author-year labels.
%%%  Per the original file header, modified copies must be renamed.
%%% ====================================================================
ENTRY
  { address
    author
    booktitle
    chapter
    edition
    editor
    doi
    eprint
    howpublished
    institution
    journal
    key
    language
    month
    note
    number
    organization
    pages
    publisher
    school
    series
    title
    type
    volume
    year
  }
  {}
  { label extra.label sort.label short.list }
INTEGERS { output.state before.all mid.sentence }
FUNCTION {init.state.consts}
{ #0 'before.all :=
  #1 'mid.sentence :=
}
STRINGS { s t }
FUNCTION {not}
{   { #0 }
    { #1 }
  if$
}
FUNCTION {and}
{   'skip$
    { pop$ #0 }
  if$
}
FUNCTION {or}
{   { pop$ #1 }
    'skip$
  if$
}
FUNCTION {field.or.null}
{ duplicate$ empty$
    { pop$ "" }
    'skip$
  if$
}
FUNCTION {emphasize}
{ duplicate$ empty$
    { pop$ "" }
    { "\emph{" swap$ * "}" * }
  if$
}
FUNCTION {n.dashify}
{ 't :=
  ""
    { t empty$ not }
    { t #1 #1 substring$ "-" =
        { t #1 #2 substring$ "--" = not
            { "--" *
              t #2 global.max$ substring$ 't :=
            }
            {   { t #1 #1 substring$ "-" = }
                { "-" *
                  t #2 global.max$ substring$ 't :=
                }
              while$
            }
          if$
        }
        { t #1 #1 substring$ *
          t #2 global.max$ substring$ 't :=
        }
      if$
    }
  while$
}
FUNCTION {tie.or.space.connect}
{ duplicate$ text.length$ #3 <
    { "~" }
    { " " }
  if$
  swap$ * *
}
FUNCTION {add.space.if.necessary}
{ duplicate$ "" =
    'skip$
    { " " * }
  if$
}
FUNCTION {either.or.check}
{ empty$
    'pop$
    { "can't use both " swap$ * " fields in " * cite$ * warning$ }
  if$
}
FUNCTION {output.nonnull}
{ 's :=
  output.state mid.sentence =
    { ", " * write$ }
    { output.state before.all =
        'write$
        { add.period$ " " * write$ }
      if$
      mid.sentence 'output.state :=
    }
  if$
  s
}
FUNCTION {output}
{ duplicate$ empty$
    'pop$
    'output.nonnull
  if$
}
FUNCTION {missing.warning}
{ "missing " swap$ * " in " * cite$ * warning$ }
FUNCTION {output.check}
{ 't :=
  duplicate$ empty$
    { pop$ t missing.warning }
    'output.nonnull
  if$
}
INTEGERS { nameptr namesleft numnames }
FUNCTION {format.language}
{ language empty$
    { "" }
    { " (" language * ")" * }
  if$
}
FUNCTION {format.names}
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
    { namesleft #0 > }
    { s nameptr "{ff~}{vv~}{ll}{, jj}" format.name$ 't :=
      nameptr #1 >
        { namesleft #1 >
            { ", " * t * }
            { numnames #2 >
                { "," * }
                'skip$
              if$
              t "others" =
                { " et~al." * }
                { " and " * t * }
              if$
            }
          if$
        }
        't
      if$
      nameptr #1 + 'nameptr :=
      namesleft #1 - 'namesleft :=
    }
  while$
}
FUNCTION {format.authors}
{ author format.names }
FUNCTION {format.editors}
{ editor empty$
    { "" }
    { editor format.names
      editor num.names$ #1 >
        { " (eds.)" * }
        { " (ed.)" * }
      if$
    }
  if$
}
FUNCTION {format.nonauthor.editors}
{ editor empty$
    { "" }
    { editor format.names
      editor num.names$ #1 >
        { ", eds." * }
        { ", ed." * }
      if$
    }
  if$
}
FUNCTION {format.title}
{ title empty$
    { "" }
    { title "t" change.case$ emphasize }
  if$
}
FUNCTION {format.eprint}
{ eprint empty$
    { "" }
    { type$ "misc" =
        { "\mbox{\href{http://arxiv.org/abs/" eprint * "}{" * eprint * "}}" * }
        { "" }
      if$
    }
  if$
}
FUNCTION {format.doi.url}
{ doi #1 #16 substring$ "https://doi.org/" =
    { doi }
    { doi #1 #7 substring$ "http://" =
        { doi }
        { "https://doi.org/" doi * }
      if$
    }
  if$
}
FUNCTION {format.journal.vol.year}
{ journal empty$
    { "journal name" missing.warning "" }
    { journal }
  if$
  volume empty$
    'skip$
    { " \textbf{" * volume * "}" * }
  if$
  year empty$
    { "year" missing.warning }
    { " (" * year * ")" * }
  if$
}
FUNCTION {format.article.journal.with.doi}
{ journal empty$
    { "journal name" missing.warning "" }
    { journal }
  if$
  volume empty$
    'skip$
    { " \textbf{" * volume * "}" * }
  if$
  number empty$
    'skip$
    { ", no.~" * number * }
  if$
  pages empty$
    { "pages" missing.warning }
    { ", " * pages n.dashify * }
  if$
  year empty$
    { "year" missing.warning }
    { " (" * year * ")" * }
  if$
  doi empty$
    'skip$
    { "\href{" format.doi.url * "}{" * swap$ * "}" * }
  if$
}
FUNCTION {format.number}
{ number empty$
    { "" }
    { "no.~" number * }
  if$
}
FUNCTION {format.date}
{ year empty$
    { month empty$
        { "" }
        { "there's a month but no year in " cite$ * warning$
          month
        }
      if$
    }
    { month empty$
        'year
        { month " " * year * }
      if$
    }
  if$
}
FUNCTION {format.bookvolume.series.number}
{ volume empty$
    { ""
      series empty$
        'skip$
        { pop$ series }
      if$
      number empty$
        'skip$
        { duplicate$ empty$
            'skip$
            { ", " * }
          if$
          "no." number tie.or.space.connect *
        }
      if$
    }
    { "vol." volume tie.or.space.connect
      number empty$
        { series empty$
            'skip$
            { series ", " * swap$ *}
          if$
        }
        { series empty$
            { "can't use both volume and number if series info is missing"
              warning$
              "in BibTeX entry type `" type$ * "'" * top$
            }
            { ", " * series * ", no." * number tie.or.space.connect }
          if$
        }
      if$
    }
  if$
}
FUNCTION {format.inproc.title.address.editors}
{ booktitle empty$
    { "" }
    { booktitle }
  if$
  address empty$
    'skip$
    { add.space.if.necessary "(" * address * ")" * }
  if$
  editor empty$
    'skip$
    { add.space.if.necessary "(" * format.nonauthor.editors * ")" * }
  if$
}
FUNCTION {format.incoll.title.editors}
{ booktitle empty$
    { "" }
    { booktitle }
  if$
  editor empty$
    'skip$
    { add.space.if.necessary "(" * format.nonauthor.editors * ")" * }
  if$
}
FUNCTION {format.number.series}
{ series empty$
    { number empty$
        { "" }
        { "there's a number but no series in " cite$ * warning$ }
      if$
    }
    { series
      number empty$
        'skip$
        { ", no.~" * number * }
      if$
    }
  if$
}
FUNCTION {format.edition}
{ edition empty$
    { "" }
    { output.state mid.sentence =
        { edition "l" change.case$ " ed." * }
        { edition "t" change.case$ " ed." * }
      if$
    }
  if$
}
INTEGERS { multiresult }
FUNCTION {multi.page.check}
{ 't :=
  #0 'multiresult :=
    { multiresult not
      t empty$ not
      and
    }
    { t #1 #1 substring$
      duplicate$ "-" =
      swap$ duplicate$ "," =
      swap$ "+" =
      or or
        { #1 'multiresult := }
        { t #2 global.max$ substring$ 't := }
      if$
    }
  while$
  multiresult
}
FUNCTION {format.pages}
{ pages empty$
    { "" }
    { pages n.dashify }
  if$
}
FUNCTION {format.book.pages}
{ pages empty$
    { "" }
    { pages multi.page.check
        { "pp.~" pages n.dashify * }
        { "p.~" pages * }
      if$
    }
  if$
}
FUNCTION {format.chapter.pages}
{ chapter empty$
    'format.pages
    { type empty$
        { "ch.~" }
        { type "l" change.case$ " " * }
      if$
      chapter *
      pages empty$
        'skip$
        { ", " * format.book.pages * }
      if$
    }
  if$
}
FUNCTION {empty.misc.check}
{ author empty$ title empty$ howpublished empty$
  month empty$ year empty$ note empty$
  and and and and and
  key empty$ not and
    { "all relevant fields are empty in " cite$ * warning$ }
    'skip$
  if$
}
FUNCTION {format.thesis.type}
{ type empty$
    'skip$
    { pop$
      type "t" change.case$
    }
  if$
}
FUNCTION {format.tr.number}
{ type empty$
    { "Tech. Report" }
    'type
  if$
  number empty$
    { "t" change.case$ }
    { number tie.or.space.connect }
  if$
}
FUNCTION {format.article.crossref}
{ key empty$
    { journal empty$
        { "need key or journal for " cite$ * " to crossref " * crossref *
          warning$
          ""
        }
        { "In " journal * }
      if$
    }
    { "In " key * }
  if$
  " \cite{" * crossref * "}" *
}
FUNCTION {format.crossref.editor}
{ editor #1 "{vv~}{ll}" format.name$
  editor num.names$ duplicate$
  #2 >
    { pop$ " et~al." * }
    { #2 <
        'skip$
        { editor #2 "{ff }{vv }{ll}{ jj}" format.name$ "others" =
            { " et~al." * }
            { " and " * editor #2 "{vv~}{ll}" format.name$ * }
          if$
        }
      if$
    }
  if$
}
FUNCTION {format.book.crossref}
{ volume empty$
    { "empty volume in " cite$ * "'s crossref of " * crossref * warning$
      "In "
    }
    { "Vol." volume tie.or.space.connect
      " of " *
    }
  if$
  editor empty$
  editor field.or.null author field.or.null =
  or
    { key empty$
        { series empty$
            { "need editor, key, or series for " cite$ * " to crossref " *
              crossref * warning$
              "" *
            }
            { series * }
          if$
        }
        { key * }
      if$
    }
    { format.crossref.editor * }
  if$
  " \cite{" * crossref * "}" *
}
FUNCTION {format.incoll.inproc.crossref}
{ editor empty$
  editor field.or.null author field.or.null =
  or
    { key empty$
        { booktitle empty$
            { "need editor, key, or booktitle for " cite$ * " to crossref " *
              crossref * warning$
              ""
            }
            { "In \emph{" booktitle * "}" * }
          if$
        }
        { "In " key * }
      if$
    }
    { "In " format.crossref.editor * }
  if$
  " \cite{" * crossref * "}" *
}
FUNCTION {format.lab.names}
{ 's :=
  s #1 "{vv~}{ll}" format.name$
  s num.names$ duplicate$
  #2 >
    { pop$ " et~al." * }
    { #2 <
        'skip$
        { s #2 "{ff }{vv }{ll}{ jj}" format.name$ "others" =
            { " et~al." * }
            { " and " * s #2 "{vv~}{ll}" format.name$ * }
          if$
        }
      if$
    }
  if$
}
FUNCTION {format.full.names}
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
    { namesleft #0 > }
    { s nameptr "{vv~}{ll}" format.name$ 't :=
      nameptr #1 >
        { namesleft #1 >
            { ", " * t * }
            { numnames #2 >
                { "," * }
                'skip$
              if$
              t "others" =
                { " et~al." * }
                { " and " * t * }
              if$
            }
          if$
        }
        't
      if$
      nameptr #1 + 'nameptr :=
      namesleft #1 - 'namesleft :=
    }
  while$
}
FUNCTION {author.full}
{ author empty$
    { "" }
    { author format.full.names }
  if$
}
FUNCTION {editor.full}
{ editor empty$
    { "" }
    { editor format.full.names }
  if$
}
FUNCTION {author.editor.full}
{ author empty$
    { editor empty$
        { "" }
        { editor format.full.names }
      if$
    }
    { author format.full.names }
  if$
}
FUNCTION {make.full.names}
{ type$ "book" =
  type$ "inbook" =
  or
    'author.editor.full
    { type$ "proceedings" =
        'editor.full
        'author.full
      if$
    }
  if$
}
FUNCTION {author.key.label}
{ author empty$
    { key empty$
        { cite$ #1 #3 substring$ }
        'key
      if$
    }
    { author format.lab.names }
  if$
}
FUNCTION {author.editor.key.label}
{ author empty$
    { editor empty$
        { key empty$
            { cite$ #1 #3 substring$ }
            'key
          if$
        }
        { editor format.lab.names }
      if$
    }
    { author format.lab.names }
  if$
}
FUNCTION {author.key.organization.label}
{ author empty$
    { key empty$
        { organization empty$
            { cite$ #1 #3 substring$ }
            { organization #1 #3 text.prefix$ }
          if$
        }
        'key
      if$
    }
    { author format.lab.names }
  if$
}
FUNCTION {editor.key.organization.label}
{ editor empty$
    { key empty$
        { organization empty$
            { cite$ #1 #3 substring$ }
            { organization #1 #3 text.prefix$ }
          if$
        }
        'key
      if$
    }
    { editor format.lab.names }
  if$
}
FUNCTION {calc.short.authors}
{ type$ "book" =
  type$ "inbook" =
  or
    'author.editor.key.label
    { type$ "proceedings" =
        'editor.key.organization.label
        { type$ "manual" =
            'author.key.organization.label
            'author.key.label
          if$
        }
      if$
    }
  if$
  'short.list :=
}
FUNCTION {calc.label}
{ calc.short.authors
  short.list
  "("
  *
  year duplicate$ empty$
    { pop$ "" }
    'skip$
  if$
  *
  'label :=
}
FUNCTION {output.bibitem}
{ newline$
  calc.label
  "\bibitem[" write$
  label write$
  ")" make.full.names duplicate$ short.list =
    { pop$ }
    { * }
  if$
  "]{" * write$
  cite$ write$
  "}" write$
  newline$
  ""
  before.all 'output.state :=
}
FUNCTION {fin.entry}
{ add.period$
  write$
  newline$
}
FUNCTION {article}
{ output.bibitem
  format.authors "author" output.check
  format.title "title" output.check
  crossref missing$
    { format.article.journal.with.doi output
    }
    { format.article.crossref output.nonnull
      format.pages output
    }
  if$
  format.language *
  format.eprint output
  note output
  fin.entry
}
FUNCTION {book}
{ output.bibitem
  author empty$
    { format.editors "author and editor" output.check }
    { format.authors output.nonnull
      crossref missing$
        { "author and editor" editor either.or.check }
        'skip$
      if$
    }
  if$
  format.title "title" output.check
  format.edition output
  crossref missing$
    { format.bookvolume.series.number output
      publisher "publisher" output.check
      address output
    }
    { format.book.crossref output.nonnull
    }
  if$
  format.date "year" output.check
  format.language *
  format.eprint output
  note output
  fin.entry
}
FUNCTION {booklet}
{ output.bibitem
  format.authors output
  format.title "title" output.check
  howpublished output
  address output
  format.date output
  format.eprint output
  note output
  fin.entry
}
FUNCTION {inbook}
{ output.bibitem
  author empty$
    { format.editors "author and editor" output.check }
    { format.authors output.nonnull
      crossref missing$
        { "author and editor" editor either.or.check }
        'skip$
      if$
    }
  if$
  title "title" output.check
  crossref missing$
    { format.bookvolume.series.number output
      format.chapter.pages "chapter and pages" output.check
      format.number.series output
      publisher "publisher" output.check
      address output
    }
    { format.chapter.pages "chapter and pages" output.check
      format.book.crossref output.nonnull
    }
  if$
  format.edition output
  format.date "year" output.check
  format.book.pages output
  format.language *
  format.eprint output
  note output
  fin.entry
}
FUNCTION {incollection}
{ output.bibitem
  format.authors "author" output.check
  format.title "title" output.check
  crossref missing$
    { format.incoll.title.editors "booktitle" output.check
      format.bookvolume.series.number output
      publisher "publisher" output.check
      address output
      format.edition output
      format.date "year" output.check
    }
    { format.incoll.inproc.crossref output.nonnull
    }
  if$
  format.eprint output
  note output
  format.book.pages output
  format.language *
  fin.entry
}
FUNCTION {inproceedings}
{ output.bibitem
  format.authors "author" output.check
  format.title "title" output.check
  crossref missing$
    { format.inproc.title.address.editors "booktitle" output.check
      format.bookvolume.series.number output
      format.book.pages output
      organization output
      publisher output
      format.date "year" output.check
    }
    { format.incoll.inproc.crossref output.nonnull
    }
  if$
  format.eprint output
  note output
  format.language *
  fin.entry
}
FUNCTION {conference} { inproceedings }
FUNCTION {manual}
{ output.bibitem
  author empty$
    { organization empty$
        'skip$
        { organization output.nonnull
          address output
        }
      if$
    }
    { format.authors output.nonnull }
  if$
  format.title "title" output.check
  author empty$
    { organization empty$
        { address output }
        'skip$
      if$
    }
    { organization output
      address output
    }
  if$
  format.edition output
  format.date output
  format.eprint output
  note output
  fin.entry
}
FUNCTION {mastersthesis}
{ output.bibitem
  format.authors "author" output.check
  format.title "title" output.check
  "Master's thesis" format.thesis.type output.nonnull
  school "school" output.check
  address output
  format.date "year" output.check
  format.eprint output
  note output
  fin.entry
}
FUNCTION {misc}
{ output.bibitem
  format.authors output
  format.title output
  howpublished output
  format.date output
  format.eprint output
  note output
  format.book.pages output
  fin.entry
  empty.misc.check
}
FUNCTION {phdthesis}
{ output.bibitem
  format.authors "author" output.check
  format.title "title" output.check
  "Ph.D. thesis" format.thesis.type output.nonnull
  school "school" output.check
  address output
  format.date "year" output.check
  format.eprint output
  note output
  format.book.pages output
  fin.entry
}
FUNCTION {proceedings}
{ output.bibitem
  editor empty$
    { organization output }
    { format.editors output.nonnull }
  if$
  format.title "title" output.check
  format.bookvolume.series.number output
  address empty$
    { editor empty$
        'skip$
        { organization output }
      if$
      publisher output
      format.date "year" output.check
    }
    { address output.nonnull
      editor empty$
        'skip$
        { organization output }
      if$
      publisher output
      format.date "year" output.check
    }
  if$
  format.eprint output
  note output
  fin.entry
}
FUNCTION {techreport}
{ output.bibitem
  format.authors "author" output.check
  format.title "title" output.check
  format.tr.number output.nonnull
  institution "institution" output.check
  address output
  format.date "year" output.check
  format.eprint output
  note output
  fin.entry
}
FUNCTION {unpublished}
{ output.bibitem
  format.authors "author" output.check
  format.title "title" output.check
  note output
  format.date output
  format.eprint output
  fin.entry
}
FUNCTION {default.type} { misc }
MACRO {jan} {"January"}
MACRO {feb} {"February"}
MACRO {mar} {"March"}
MACRO {apr} {"April"}
MACRO {may} {"May"}
MACRO {jun} {"June"}
MACRO {jul} {"July"}
MACRO {aug} {"August"}
MACRO {sep} {"September"}
MACRO {oct} {"October"}
MACRO {nov} {"November"}
MACRO {dec} {"December"}
READ
FUNCTION {sortify}
{ purify$
  "l" change.case$
}
INTEGERS { len }
FUNCTION {chop.word}
{ 's :=
  'len :=
  s #1 len substring$ =
    { s len #1 + global.max$ substring$ }
    's
  if$
}
FUNCTION {sort.format.names}
{ 's :=
  #1 'nameptr :=
  ""
  s num.names$ 'numnames :=
  numnames 'namesleft :=
    { namesleft #0 > }
    { nameptr #1 >
        { "   " * }
        'skip$
      if$
      s nameptr "{vv{ } }{ll{ }}{  ff{ }}{  jj{ }}" format.name$ 't :=
      nameptr numnames = t "others" = and
        { "et al" * }
        { t sortify * }
      if$
      nameptr #1 + 'nameptr :=
      namesleft #1 - 'namesleft :=
    }
  while$
}
FUNCTION {begin.bib}
{ preamble$ empty$
    'skip$
    { preamble$ write$ newline$ }
  if$
  "\begin{thebibliography}{99}" write$ newline$
}
EXECUTE {begin.bib}
EXECUTE {init.state.consts}
ITERATE {call.type$}
FUNCTION {end.bib}
{ newline$
  "\end{thebibliography}" write$ newline$
}
EXECUTE {end.bib}
