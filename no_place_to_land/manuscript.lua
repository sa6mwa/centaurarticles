-- Keep the abstract on the cover and the remaining manuscript in the body.
local art_before = {
  ['co-invention-why-technology-is-never-the-whole-system'] = {command='FactoryRetrofitArt', wide=true},
  ['ai-inside-yesterdays-organization'] = {command='CoInventionArt', wide=true},
  ['different-economic-outcomes'] = {command='MeasurementArt'},
  ['beyond-tasks-organizational-recomposition'] = {command='ProductionComparisonArt', wide=true},
  ['no-place-to-land-1'] = {command='RecompositionArt', wide=true},
  ['markets-built-around-the-old-unit-of-production'] = {command='FragmentedAssignmentArt'},
  ['the-applied-technology-gap'] = {command='ComplementaryAssetsArt', wide=true},
  ['building-where-the-future-can-reach-you'] = {command='ReusableCoInventionArt', wide=true},
  ['conclusion-from-coordination-to-conversion'] = {command='HandoverArt', wide=true},
}
function Pandoc(doc)
  local part = pandoc.utils.stringify(doc.meta.part)
  local result = pandoc.List()
  local in_abstract = false
  local in_body = false
  local columns_open = false
  for _, block in ipairs(doc.blocks) do
    if block.t == 'Header' and block.level == 2 then
      local heading = pandoc.utils.stringify(block.content)
      in_abstract = heading == 'Abstract'
      if heading == 'Introduction' then in_body = true end
    end
    if part == 'abstract' and in_abstract and block.t ~= 'Header' then
      result:insert(block)
    elseif part == 'body' and in_body then
      -- Markdown H2/H3 become article sections/subsections.
      if block.t == 'Header' then
        local art = art_before[block.identifier]
        if block.level == 2 then
          if columns_open then
            if art and not art.wide then
              result:insert(pandoc.RawBlock('latex', '\\' .. art.command))
            end
            result:insert(pandoc.RawBlock('latex', '\\end{multicols}'))
          end
          if art and art.wide then
            result:insert(pandoc.RawBlock('latex', '\\' .. art.command))
          end
          result:insert(pandoc.RawBlock('latex', '\\clearpage\n\\begin{multicols}{2}'))
          columns_open = true
        elseif art then
          result:insert(pandoc.RawBlock('latex', '\\' .. art.command))
        end
        -- Preserve the deliberate next-column start in the chapter layout.
        if block.identifier == 'when-the-producer-moves-ahead' then
          result:insert(pandoc.RawBlock('latex', '\\columnbreak'))
        end
        block.level = block.level - 1
      end
      result:insert(block)
    end
  end
  if columns_open then result:insert(pandoc.RawBlock('latex', '\\end{multicols}')) end
  if part ~= 'abstract' and part ~= 'body' then
    error('Select -M part=abstract or -M part=body')
  end
  if #result == 0 then error('The requested manuscript part is empty') end
  return pandoc.Pandoc(result)
end
