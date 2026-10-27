-- Prose stays in Markdown. This editorial map places complete paragraphs in
-- columns, with deliberate section openings, pull quotes and original art.
function Pandoc(doc)
  local part = pandoc.utils.stringify(doc.meta.part)
  if part ~= 'abstract' and part ~= 'body' then
    error('Select -M part=abstract or -M part=body')
  end
  local result = pandoc.List()
  local sections, current = {}, nil
  for _, block in ipairs(doc.blocks) do
    if block.t == 'Header' and block.level == 2 then
      current = {header = block, blocks = {}}
      table.insert(sections, current)
    elseif current then
      table.insert(current.blocks, block)
    end
  end
  local function raw(text) result:insert(pandoc.RawBlock('latex', text)) end
  local function paragraphs(s, first, last)
    for i = first, last do result:insert(s.blocks[i]) end
  end
  local function columns(s, first, split, last)
    raw('\\begin{EssayColumns}')
    paragraphs(s, first, split)
    raw('\\NextEssayColumn')
    paragraphs(s, split + 1, last)
    raw('\\end{EssayColumns}')
  end
  local function quote(text) raw('\\PullQuote{' .. text .. '}') end
  local expected = {
    {'introduction', 3},
    {'the-missing-return-has-an-organizational-address', 7},
    {'the-unit-of-work-has-changed', 6},
    {'why-the-company-keeps-paying', 6},
    {'give-the-whole-outcome-an-owner', 11},
    {'safety-must-be-able-to-act', 5},
    {'stop-financing-the-obstruction', 3},
  }
  local body_index = 0
  for _, s in ipairs(sections) do
    local abstract = pandoc.utils.stringify(s.header.content) == 'Abstract'
    if abstract and part == 'abstract' then
      paragraphs(s, 1, #s.blocks)
    elseif not abstract and part == 'body' then
      body_index = body_index + 1
      local page = expected[body_index]
      if not page or s.header.identifier ~= page[1] or #s.blocks ~= page[2] then
        error('Editorial layout needs review: section order or paragraph count changed in ' .. s.header.identifier)
      end
      if body_index > 1 then raw('\\clearpage') end
      s.header.level = 1
      result:insert(s.header)
      if body_index == 1 then
        raw('\\begin{OpeningLead}')
        paragraphs(s, 1, 1)
        raw('\\end{OpeningLead}')
        columns(s, 2, 2, 3)
        raw('\\EssayArt{opening-illustration.png}')
      elseif body_index == 2 then
        paragraphs(s, 1, 1)
        raw('\\vspace{4mm}')
        columns(s, 2, 3, 4)
        raw('\\SurveyFigure')
        raw('\\ContinuedSection{The missing return has an organizational address}')
        columns(s, 5, 5, 6)
        raw('\\PortfolioFigure')
        raw('\\vspace{7mm}')
        paragraphs(s, 7, 7)
      elseif body_index == 3 then
        columns(s, 1, 3, 6)
        raw('\\EssayArt{unit-comic.png}')
      elseif body_index == 4 then
        columns(s, 1, 3, 6)
        quote('The institution can afford the delay while the useful work remains undone.')
      elseif body_index == 5 then
        columns(s, 1, 1, 2)
        quote('A unit that must seek fresh agreement across departments for every meaningful action has responsibility without control.')
        columns(s, 3, 3, 4)
        raw('\\vspace{6mm}')
        paragraphs(s, 5, 5)
        raw('\\ContinuedSection{Give the whole outcome an owner}')
        columns(s, 6, 8, 11)
        raw('\\OutcomeFigure')
      elseif body_index == 6 then
        columns(s, 1, 3, 5)
        raw('\\SafetyFigure')
      elseif body_index == 7 then
        columns(s, 1, 1, 2)
        quote('We cannot keep paying capable people to wait and expect abundance to emerge from the queue.')
        paragraphs(s, 3, 3)
        raw('\\EssayArt{closing-illustration.png}')
      end
    end
  end
  if #result == 0 then error('The requested manuscript part is empty') end
  return pandoc.Pandoc(result)
end
