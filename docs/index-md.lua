-- Pandoc filter for index.md, the Markdown copy of index.tex, for GitHub.
-- Puts the title on top as the only level-1 heading, points the PDF links into build/
-- (where the PDFs are built), and closes with a line saying where the file comes from.

function Header(el)
  el.level = el.level + 1  -- sections sit under the title
  return el
end

function Link(el)
  if el.target:match("%.pdf$") then
    el.target = "build/" .. el.target
  end
  return el
end

function Pandoc(doc)
  -- The title's line break becomes a colon: "Altair 8800 replica on a Tang Nano 9K: Write-ups"
  local title = pandoc.Inlines(doc.meta.title or {}):walk({
    LineBreak = function() return {pandoc.Str(":"), pandoc.Space()} end,
  })
  table.insert(doc.blocks, 1, pandoc.Header(1, title))
  table.insert(doc.blocks, pandoc.Para({pandoc.Emph(pandoc.Inlines(
    "Generated from index.tex by build.sh, which also builds the PDFs into build/. Edit index.tex, not this file."))}))
  return doc
end
