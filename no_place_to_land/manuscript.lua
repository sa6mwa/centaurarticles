-- Keep the abstract on the cover and the remaining manuscript in the body.
function Pandoc(doc)
  local part = pandoc.utils.stringify(doc.meta.part)
  local result = pandoc.List()
  local in_abstract = false
  local in_body = false
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
        -- In the two-column essay, newpage advances to the next column.
        if block.identifier == 'when-the-producer-moves-ahead' then
          result:insert(pandoc.RawBlock('latex', '\\newpage'))
        end
        block.level = block.level - 1
      end
      result:insert(block)
    end
  end
  if part ~= 'abstract' and part ~= 'body' then
    error('Select -M part=abstract or -M part=body')
  end
  if #result == 0 then error('The requested manuscript part is empty') end
  return pandoc.Pandoc(result)
end
