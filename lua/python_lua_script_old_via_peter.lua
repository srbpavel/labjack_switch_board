print("start")
local count = 0
local mb_write = MB.W

mb_write(46000, 3, 1000) --user_ram_0_f32 -> 46000 to 1000, be used via timer

delay = 200 -- 1000ms=1sec

LJ.IntervalConfig(0, delay)
local check_interval = LJ.CheckInterval

local out_pin = 2005 -- FIO5 -> 2005
local led_state = 1

while true do
  if check_interval(0) then
    --TEST / do tohohle registru budu psat pythonem
    LJ.IntervalConfig(0, MB.R(46000, 3)) --read delay from user_ram_1
    mb_write(out_pin, 0, 1) -- address / data_type / value
    print("led: ", led_state)
    
    if led_state == 1 then
      mb_write(46002, 3, 200) --user_ram_1_f32 -> 46002 to 200 [our delay]
      mb_write(out_pin, 0, 1) --ON for next cycle
      led_state = 0
    else
      mb_write(46002, 3, 0)
      mb_write(out_pin, 0, 0) --OFF for next cycle
      led_state = 1
    end
  end
end
