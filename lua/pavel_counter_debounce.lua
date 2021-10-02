print("counter + debounce:")

local debounce_int = 100 --100 ms
local mb_read = MB.R
local mb_write = MB.W

local edge = 1 --SET FOR 1 rising
--local edge = 0 --0 falling EDGE

local bits = 0
local bits_new = 99
local count = 0 
local count_debounce = 0
local increment_recent = 0

--LUA PERFORMANCE FUNCTIONS
local throttle_setting = 100 --throttle = (3* number of code lines) + 20
LJ.setLuaThrottle(throttle_setting)
local throttle_setting = LJ.getLuaThrottle()
print("current lua throttle setting: ", throttle_setting)

LJ.IntervalConfig(0, debounce_int)
local check_interval = LJ.CheckInterval

while true do
  bits_new = mb_read(2004, 0) --FIO4 -> 2004 / return 0 or 1
  
  if bits ~= bits_new then
    if edge == 1 then
      if bits == 0 then
        count = count + 1
      end
    else
      if bits == 1 then
        count = count + 1
      end
    end
    bits = bits_new
  end
  
  --DEBOUNCE
  if check_interval(0) then
    if increment_recent == 0 then
      if count > count_debounce then
        increment_recent = 1
        count_debounce = count_debounce + 1
        count = count_debounce
        if edge == 1 then
          print("rissing total: ", count)
        else
          print("falling total: ", count)
        end  
        --mb_write(46000, 3, count_debounce) --save in USER_RAM / can be read via Python later
      end
    else
      count = count_debounce
      increment_recent = 0
    end
  end
end
