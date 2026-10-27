-- The manuscript owns prose; the cover and figure placement belong to layout.
local art_before = {
  ['the-missing-return-has-an-organizational-address'] = 'SurveyFigure',
  ['give-the-whole-outcome-an-owner'] = 'OutcomeFigure',
}

function Pandoc(doc)
  local part = pandoc.utils.stringify(doc.meta.part)
  if part ~= 'abstract' and part ~= 'body' then
    error('Select -M part=abstract or -M part=body')
  end
  local result = pandoc.List()
  local current = nil
  for _, block in ipairs(doc.blocks) do
    if block.t == 'Header' and block.level == 2 then
      local heading = pandoc.utils.stringify(block.content)
      current = heading == 'Abstract' and 'abstract' or 'body'
    end
    if current == part then
      if block.t == 'Header' then
        if part == 'body' then
          if art_before[block.identifier] then
            result:insert(pandoc.RawBlock('latex', '\\' .. art_before[block.identifier]))
          end
          if block.identifier == 'stop-financing-the-obstruction' then
            result:insert(pandoc.RawBlock('latex', '\\balance'))
          end
          block.level = block.level - 1
          result:insert(block)
        end
      else
        result:insert(block)
      end
    end
  end
  if #result == 0 then error('The requested manuscript part is empty') end
  return pandoc.Pandoc(result)
end
