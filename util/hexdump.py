"""hexdump.py"""

def hexDump( data, msg=None, logFunc=print):
  """ dump data in hex format """
  def isprint(ch):
    val = ord(ch)
    return (val > 31 and val < 127)
  
  hex = ''
  str = ''
  index = 0
  offset = 0
  CHARS_PER_LINE = 16
  hdr = ''
  if msg:
    hdr = msg + ' - '
  for ch in data:
    hex += '%02X ' % ord(ch)
    if isprint(ch):
      str += ch
    else:
      str += '.'
    index += 1
    if index % CHARS_PER_LINE == 0:
      logFunc( '%s%3d : %-48s %s' % (hdr, offset, hex, str))
      hex = ''
      str = ''
      offset += CHARS_PER_LINE
  if hex != '':
    logFunc( '%s%3d : %-48s %s' % (hdr, offset, hex, str) )

