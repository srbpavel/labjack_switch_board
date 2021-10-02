print("counter [without debounce]:")

local mb_read = MB.R
local mb_write = MB.W

--local edge = 1 -- SET FOR 1 rising
local edge = 0 -- 0 falling EDGE

local bits = 0
local bits_new = 99
local count = 0 

-- LUA PERFORMANCE FUNCTIONS
local throttle_setting = 100 -- throttle = (3* number of code lines) + 20
LJ.setLuaThrottle(throttle_setting)
local throttle_setting = LJ.getLuaThrottle()
print("current lua throttle setting: ", throttle_setting)

while true do
  bits_new = mb_read(2004, 0) -- FIO4 -> 2004 / return 0 or 1
  
  if bits ~= bits_new then
    
    if edge == 1 then
      if bits == 0 then
        count = count + 1
        print("rissing total: ", count)
      end
    else
      if bits == 1 then
        count = count + 1
        print("falling total: ", count)
      end
    end

    bits = bits_new
    mb_write(46000, 3, count) --save in USER_RAM / can be read via Python later
  end
end
